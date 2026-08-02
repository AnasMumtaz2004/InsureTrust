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
    """Node representing human-in-the-loop pause point for adjudicator approval/override."""
    action = state.get("human_approval_action")
    if action == "APPROVE":
        final_dec = dict(state.get("final_decision", {}))
        final_dec["human_overridden"] = False
        final_dec["approved_by"] = "ADJUDICATOR_HUMAN"
        return {"final_decision": final_dec, "status": "APPROVED", "last_completed_agent": "human_review_interrupt"}
    elif action == "OVERRIDE":
        final_dec = dict(state.get("final_decision", {}))
        final_dec["human_overridden"] = True
        final_dec["override_reason"] = state.get("human_adjudicator_notes", "Overridden by human adjudicator.")
        final_dec["decision_type"] = "APPROVE"
        return {"final_decision": final_dec, "status": "OVERRIDDEN", "last_completed_agent": "human_review_interrupt"}
    else:
        return {"status": "PAUSED_FOR_HUMAN_REVIEW"}

def finalize_decision_node(state: ClaimAdjudicationState) -> Dict[str, Any]:
    """Final node completing the claims graph execution."""
    final_dec = state.get("final_decision") or state.get("draft_decision") or {}
    logger.info(f"Finalizing claim {state.get('claim_id')} with decision: {final_dec.get('decision_type', 'PENDING')}")
    return {
        "status": f"COMPLETED_{final_dec.get('decision_type', 'APPROVED')}",
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
