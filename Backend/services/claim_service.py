import uuid
import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from graph.main_graph import claims_graph
from database.models import Claim, Decision, DebateTranscript
from database.enums import ClaimStatus, map_decision_to_status
from services.audit_service import AuditService
from services.notification_service import NotificationService
from utils.logger import logger


class ClaimService:
    """Business logic service gluing API endpoints to LangGraph execution and ORM persistence."""

    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
        self.notification_service = NotificationService()

    def submit_and_process_claim(self, claim_input: Dict[str, Any]) -> Dict[str, Any]:
        """Creates claim DB record and executes the multi-agent claims graph."""
        claim_id = f"CLM-{uuid.uuid4().hex[:8].upper()}"
        claim_number = f"CN-{datetime.datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        # 1. Create DB Claim entity
        db_claim = Claim(
            id=claim_id,
            claim_number=claim_number,
            claimant_id=claim_input.get("claimant_id", "USR-1001"),
            policy_number=claim_input.get("policy_number", "POL-DEFAULT"),
            status="IN_REVIEW",
            total_claimed_amount=float(claim_input.get("claimed_amount", 0.0))
        )
        self.db.add(db_claim)
        self.db.commit()
        self.db.refresh(db_claim)

        # 2. Build initial graph state
        initial_state = {
            "claim_id": claim_id,
            "policy_number": claim_input.get("policy_number"),
            "claimant_id": claim_input.get("claimant_id"),
            "product_line": claim_input.get("product_line", "HEALTH"),
            "incident_date": claim_input.get("incident_date"),
            "claimed_amount": float(claim_input.get("claimed_amount", 0.0)),
            "diagnosis_codes": claim_input.get("diagnosis_codes", []),
            "procedure_codes": claim_input.get("procedure_codes", []),
            "description": claim_input.get("description", "")
        }

        thread_config = {"configurable": {"thread_id": claim_id}}
        logger.info(f"Triggering LangGraph claims adjudication workflow for claim {claim_id}")

        # 3. Stream graph execution (stops at interrupt_before=human_review_interrupt if required)
        final_state = initial_state
        for event in claims_graph.stream(initial_state, thread_config):
            for node_name, node_output in event.items():
                logger.info(f"Node '{node_name}' finished for Claim {claim_id}")
                self.audit_service.log_step(claim_id, agent_name=node_name, action="NODE_EXECUTED", snapshot=node_output)

        # 4. Read final state snapshot from checkpointer
        current_state_snapshot = claims_graph.get_state(thread_config).values
        if current_state_snapshot:
            final_state.update(current_state_snapshot)

        # Update DB models based on final graph state
        db_claim.complexity_score = final_state.get("complexity_score")

        if final_state.get("human_review_required"):
            # Graph paused before human_review_interrupt.
            # Store PENDING_APPROVAL with the draft approved_amount (not 0).
            db_claim.status = ClaimStatus.PENDING_APPROVAL.value
            draft_approved = float(final_state.get("approved_amount", 0.0))
            db_claim.approved_amount = draft_approved

            # Create a pending Decision row so the row exists before resume.
            draft_dec = final_state.get("final_decision") or final_state.get("draft_decision") or {}
            decision_rec = Decision(
                id=f"DEC-{uuid.uuid4().hex[:8].upper()}",
                claim_id=claim_id,
                decision_type=draft_dec.get("decision_type", "APPROVE"),
                rationale=draft_dec.get("rationale", "Automated multi-agent decision pending human review."),
                itemized_payout=draft_dec.get("itemized_payout"),
                compliance_status="PENDING_REVIEW",
                approved_by=None,
                human_overridden=False,
            )
            self.db.add(decision_rec)
        else:
            final_dec = final_state.get("final_decision") or final_state.get("draft_decision") or {}
            db_claim.status = map_decision_to_status(
                final_dec.get("decision_type", "APPROVE")
            ).value
            db_claim.approved_amount = float(final_state.get("approved_amount", 0.0))
            db_claim.completed_at = datetime.datetime.utcnow()

            # Store Decision ORM record
            decision_rec = Decision(
                id=f"DEC-{uuid.uuid4().hex[:8].upper()}",
                claim_id=claim_id,
                decision_type=final_dec.get("decision_type", "APPROVE"),
                rationale=final_dec.get("rationale", "Automated multi-agent decision."),
                itemized_payout=final_dec.get("itemized_payout"),
                approved_by="AUTO_SYSTEM"
            )
            self.db.add(decision_rec)

        # Store Debate transcript if generated
        if final_state.get("debate_transcript"):
            dt = final_state.get("debate_transcript")
            transcript_rec = DebateTranscript(
                id=f"DEB-{uuid.uuid4().hex[:8].upper()}",
                claim_id=claim_id,
                pro_approval_arguments=dt.get("pro_approval_view"),
                pro_denial_arguments=dt.get("pro_denial_view"),
                reconciliation_summary=dt.get("synthesis"),
                confidence_delta=float(final_state.get("confidence_delta", 0.0))
            )
            self.db.add(transcript_rec)

        self.db.commit()
        self.db.refresh(db_claim)

        # 5. Dispatch async status notification
        self.notification_service.send_status_update(claim_id, db_claim.status)

        return {
            "claim_id": claim_id,
            "claim_number": claim_number,
            "status": db_claim.status,
            "state": final_state
        }

    def resume_human_review(
        self,
        claim_id: str,
        action: str,
        notes: str,
        actor_id: str,
        modified_payout: Optional[float] = None,
        decision_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Resumes a paused LangGraph execution after an adjudicator acts.

        Raises:
            ValueError("No checkpoint found for claim …")     – mapped to 404 in the route.
            ValueError("Claim is not awaiting human review")   – mapped to 409 in the route.
        """
        thread_config = {"configurable": {"thread_id": claim_id}}

        # --- 1. Verify a checkpoint exists ---
        checkpoint = claims_graph.get_state(thread_config)
        if not checkpoint or not checkpoint.values:
            raise ValueError(f"No checkpoint found for claim {claim_id}")

        # --- 2. Verify the graph is actually paused at human_review_interrupt ---
        next_nodes = list(checkpoint.next) if checkpoint.next else []
        if "human_review_interrupt" not in next_nodes:
            raise ValueError("Claim is not awaiting human review")

        # --- 3. Inject the human payload as orchestration_agent so the
        #         conditional edge re-evaluates and routes to human_review_interrupt.
        #         This does NOT mark human_review_interrupt as done. ---
        resume_payload: Dict[str, Any] = {
            "human_approval_action": action,
            "human_adjudicator_notes": notes,
            "human_actor_id": actor_id,
            # Keep last_completed_agent as "compliance_guardrail" so orchestration
            # routes back to human_review_interrupt on the next tick.
            # We inject into the current interrupted position directly.
        }
        if modified_payout is not None:
            resume_payload["human_modified_payout"] = modified_payout
        if decision_type is not None:
            resume_payload["human_decision_type"] = decision_type
        elif action == "APPROVE":
            resume_payload["human_decision_type"] = "APPROVE"
        elif action == "OVERRIDE":
            resume_payload["human_decision_type"] = decision_type or "APPROVE"

        # Update state *as the node that is currently interrupted* so LangGraph
        # resumes from human_review_interrupt itself (not skipping it).
        claims_graph.update_state(thread_config, resume_payload, as_node="orchestration_agent")

        # --- 4. Stream to let human_review_interrupt and finalize_decision run ---
        for event in claims_graph.stream(None, thread_config):
            for node_name, node_output in event.items():
                logger.info(f"Resume: node '{node_name}' finished for Claim {claim_id}")
                self.audit_service.log_step(
                    claim_id, agent_name=node_name,
                    action=f"RESUMED_{action}", snapshot=node_output
                )

        # --- 5. Read final state (single source of truth) ---
        final_state = claims_graph.get_state(thread_config).values or {}

        # --- 6. Persist to DB in one transaction ---
        db_claim = self.db.query(Claim).filter(Claim.id == claim_id).first()
        if not db_claim:
            raise ValueError(f"Claim {claim_id} not found in database")

        # Derive DB status from action
        if action == "APPROVE":
            final_dtype = (final_state.get("final_decision") or {}).get("decision_type", "APPROVE")
            db_claim.status = map_decision_to_status(final_dtype).value
        elif action == "OVERRIDE":
            db_claim.status = ClaimStatus.OVERRIDDEN.value
        elif action == "SEND_BACK":
            db_claim.status = ClaimStatus.SENT_BACK.value
        else:
            db_claim.status = ClaimStatus.OVERRIDDEN.value
        db_claim.completed_at = datetime.datetime.utcnow()

        # approved_amount from the resolved graph state
        db_claim.approved_amount = float(final_state.get("approved_amount", db_claim.approved_amount))

        # Update the pending Decision row created at submit time
        pending_decision = (
            self.db.query(Decision)
            .filter(Decision.claim_id == claim_id, Decision.compliance_status == "PENDING_REVIEW")
            .order_by(Decision.created_at.desc())
            .first()
        )

        final_dec = final_state.get("final_decision") or {}

        if pending_decision:
            pending_decision.decision_type = final_dec.get("decision_type", pending_decision.decision_type)
            pending_decision.rationale = final_dec.get("rationale", pending_decision.rationale)
            pending_decision.itemized_payout = final_dec.get("itemized_payout", pending_decision.itemized_payout)
            pending_decision.approved_by = actor_id
            pending_decision.human_overridden = bool(final_dec.get("human_overridden", False))
            pending_decision.override_reason = final_dec.get("override_reason") or final_dec.get("sent_back_reason")
            if action == "SEND_BACK":
                pending_decision.compliance_status = "SENT_BACK"
            else:
                pending_decision.compliance_status = "PASSED"
        else:
            # Fallback: create a new Decision row if no pending one exists
            new_dec = Decision(
                id=f"DEC-{uuid.uuid4().hex[:8].upper()}",
                claim_id=claim_id,
                decision_type=final_dec.get("decision_type", "APPROVE"),
                rationale=final_dec.get("rationale", "Human adjudicator decision."),
                itemized_payout=final_dec.get("itemized_payout"),
                compliance_status="SENT_BACK" if action == "SEND_BACK" else "PASSED",
                approved_by=actor_id,
                human_overridden=bool(final_dec.get("human_overridden", False)),
                override_reason=final_dec.get("override_reason") or final_dec.get("sent_back_reason"),
            )
            self.db.add(new_dec)

        self.db.commit()
        self.db.refresh(db_claim)

        # 7. Notify
        self.notification_service.send_status_update(claim_id, db_claim.status)

        return {
            "claim_id": claim_id,
            "status": db_claim.status,
            "final_state": final_state,
        }
