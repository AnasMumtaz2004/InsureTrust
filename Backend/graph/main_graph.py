from typing import Dict, Any
from langgraph.graph import StateGraph, END
from graph.shared_state import ClaimAdjudicationState
from graph.checkpoints import get_checkpointer
from utils.logger import logger

# Import all 8 agent subgraphs and the central routing authority function
from agents.orchestration_agent.graph import orchestration_node, route_next_agent
from agents.intake_agent.graph import intake_node
from agents.policy_interpretation_agent.graph import policy_interpretation_node
from agents.medical_billing_agent.graph import medical_billing_node
from agents.precedent_agent.graph import precedent_node
from agents.debate_agent.graph import debate_agent_subgraph
from agents.decision_drafting_agent.graph import decision_drafting_node
from agents.compliance_guardrail_agent.graph import compliance_guardrail_node


def human_review_interrupt_node(state: ClaimAdjudicationState) -> Dict[str, Any]:
    """Node representing human-in-the-loop pause point for adjudicator approval/override.

    Actions:
      APPROVE   – keep the draft decision and payout; mark human_overridden=False.
      OVERRIDE  – set human_overridden=True; use human_modified_payout / human_decision_type
                  if provided, otherwise keep the draft values.
      SEND_BACK – terminal; status=SENT_BACK, no payout change, decision kept as draft
                  with sent_back=True.
    """
    action = state.get("human_approval_action", "")
    actor_id = state.get("human_actor_id", "ADJUDICATOR_HUMAN")
    notes = state.get("human_adjudicator_notes", "")

    # Base final decision from compliance agent (which copied it from draft)
    base_final = dict(state.get("final_decision") or state.get("draft_decision") or {})
    draft_approved_amount = float(state.get("approved_amount", 0.0))

    if action == "APPROVE":
        final_dec = dict(base_final)
        if state.get("human_decision_type"):
            final_dec["decision_type"] = state["human_decision_type"]
        else:
            final_dec["decision_type"] = "APPROVE"
        final_dec["human_overridden"] = False
        final_dec["approved_by"] = actor_id
        approved_amount = draft_approved_amount
        return {
            "final_decision": final_dec,
            "approved_amount": approved_amount,
            "status": "APPROVED",
            "last_completed_agent": "human_review_interrupt",
        }

    elif action == "OVERRIDE":
        final_dec = dict(base_final)
        final_dec["human_overridden"] = True
        final_dec["override_reason"] = notes
        final_dec["approved_by"] = actor_id

        # Apply human-specified decision type if provided
        human_dtype = state.get("human_decision_type")
        if human_dtype:
            final_dec["decision_type"] = human_dtype
        elif final_dec.get("decision_type") is None:
            final_dec["decision_type"] = "APPROVE"

        # Apply modified payout; DENY -> 0
        modified_payout = state.get("human_modified_payout")
        if modified_payout is not None:
            approved_amount = float(modified_payout)
        elif final_dec.get("decision_type") == "DENY":
            approved_amount = 0.0
        else:
            approved_amount = draft_approved_amount

        final_dec["approved_amount"] = approved_amount

        return {
            "final_decision": final_dec,
            "approved_amount": approved_amount,
            "status": "OVERRIDDEN",
            "last_completed_agent": "human_review_interrupt",
        }

    elif action == "SEND_BACK":
        final_dec = dict(base_final)
        final_dec["sent_back"] = True
        final_dec["sent_back_reason"] = notes
        return {
            "final_decision": final_dec,
            "approved_amount": draft_approved_amount,
            "status": "SENT_BACK",
            "last_completed_agent": "human_review_interrupt",
        }

    else:
        # Should not reach here due to schema validation, but safe fallback
        return {"status": "PAUSED_FOR_HUMAN_REVIEW"}


def finalize_decision_node(state: ClaimAdjudicationState) -> Dict[str, Any]:
    """Final node completing the claims graph execution."""
    final_dec = state.get("final_decision") or state.get("draft_decision") or {}
    logger.info(f"Finalizing claim {state.get('claim_id')} with decision: {final_dec.get('decision_type', 'PENDING')}")

    # SENT_BACK stays as-is; all other decisions get COMPLETED_ prefix
    current_status = state.get("status", "")
    if current_status == "SENT_BACK":
        terminal_status = "SENT_BACK"
    else:
        terminal_status = f"COMPLETED_{final_dec.get('decision_type', 'APPROVED')}"

    return {
        "status": terminal_status,
        "final_decision": final_dec,
        "last_completed_agent": "finalize_decision"
    }


def create_claims_adjudication_graph():
    """Thin composition file wiring all 8 subgraphs. All routing decisions are delegated to Orchestration Agent."""
    builder = StateGraph(ClaimAdjudicationState)

    # Register all 8 agent nodes + system terminal nodes
    builder.add_node("orchestration_agent", orchestration_node)
    builder.add_node("intake_agent", intake_node)
    builder.add_node("policy_interpretation", policy_interpretation_node)
    builder.add_node("medical_billing", medical_billing_node)
    builder.add_node("precedent_agent", precedent_node)
    builder.add_node("debate_agent", debate_agent_subgraph)
    builder.add_node("decision_drafting", decision_drafting_node)
    builder.add_node("compliance_guardrail", compliance_guardrail_node)
    builder.add_node("human_review_interrupt", human_review_interrupt_node)
    builder.add_node("finalize_decision", finalize_decision_node)

    # Set Orchestration Agent as single entrypoint & routing authority
    builder.set_entry_point("orchestration_agent")

    # Authoritative conditional edge out of Orchestration Agent
    builder.add_conditional_edges("orchestration_agent", route_next_agent, {
        "intake_agent": "intake_agent",
        "policy_interpretation": "policy_interpretation",
        "medical_billing": "medical_billing",
        "precedent_agent": "precedent_agent",
        "debate_agent": "debate_agent",
        "decision_drafting": "decision_drafting",
        "compliance_guardrail": "compliance_guardrail",
        "human_review_interrupt": "human_review_interrupt",
        "finalize_decision": "finalize_decision"
    })

    # All worker agents report back to Orchestration Agent after completion
    builder.add_edge("intake_agent", "orchestration_agent")
    builder.add_edge("policy_interpretation", "orchestration_agent")
    builder.add_edge("medical_billing", "orchestration_agent")
    builder.add_edge("precedent_agent", "orchestration_agent")
    builder.add_edge("debate_agent", "orchestration_agent")
    builder.add_edge("decision_drafting", "orchestration_agent")
    builder.add_edge("compliance_guardrail", "orchestration_agent")

    # Terminal edges
    builder.add_edge("human_review_interrupt", "finalize_decision")
    builder.add_edge("finalize_decision", END)

    # Compile graph with checkpointer
    checkpointer = get_checkpointer()
    graph = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["human_review_interrupt"]
    )
    return graph

# Expose compiled claims graph singleton
claims_graph = create_claims_adjudication_graph()
