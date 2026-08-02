import uuid
import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from graph.main_graph import claims_graph
from database.models import Claim, Decision, DebateTranscript
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

        # 3. Stream graph execution
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
            db_claim.status = "PENDING_APPROVAL"
        else:
            final_dec = final_state.get("final_decision") or final_state.get("draft_decision") or {}
            db_claim.status = final_dec.get("decision_type", "APPROVED")
            db_claim.approved_amount = float(final_state.get("approved_amount", 0.0))

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

    def resume_human_review(self, claim_id: str, action: str, notes: str, modified_payout: Optional[float] = None) -> Dict[str, Any]:
        """Resumes a paused LangGraph execution after an adjudicator approves/overrides."""
        thread_config = {"configurable": {"thread_id": claim_id}}
        state_values = claims_graph.get_state(thread_config).values

        if not state_values:
            raise ValueError(f"No checkpoint found for claim {claim_id}")

        resume_payload = {
            "human_approval_action": action,
            "human_adjudicator_notes": notes
        }
        if modified_payout is not None:
            resume_payload["approved_amount"] = modified_payout

        claims_graph.update_state(thread_config, resume_payload, as_node="human_review_interrupt")

        # Resume execution
        for event in claims_graph.stream(None, thread_config):
            logger.info(f"Resumed graph execution event: {event}")

        final_state = claims_graph.get_state(thread_config).values

        # Update DB claim status
        db_claim = self.db.query(Claim).filter(Claim.id == claim_id).first()
        if db_claim:
            db_claim.status = "APPROVED" if action == "APPROVE" else "OVERRIDDEN"
            if modified_payout is not None:
                db_claim.approved_amount = modified_payout
            self.db.commit()

        return {
            "claim_id": claim_id,
            "status": db_claim.status if db_claim else "COMPLETED",
            "final_state": final_state
        }
