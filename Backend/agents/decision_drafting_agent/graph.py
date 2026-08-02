from typing import Dict, Any
from agents.decision_drafting_agent.tools import format_legal_citations, compute_final_payout_schedule

def decision_drafting_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node execution function for Decision Drafting Agent."""
    claim_id = state.get("claim_id", "UNKNOWN")
    claimed = float(state.get("claimed_amount", 0.0))
    allowed = float(state.get("allowed_total", 0.0))
    reconciled_rec = state.get("reconciliation_recommendation", "")
    coverage = state.get("coverage_status", "")
    mismatches = state.get("code_mismatches", [])

    if reconciled_rec:
        decision_type = reconciled_rec
    elif coverage == "EXCLUDED" or len(mismatches) > 1:
        decision_type = "DENY"
    elif allowed < claimed and allowed > 0:
        decision_type = "PARTIAL_APPROVE"
    else:
        decision_type = "APPROVE"

    payout_info = compute_final_payout_schedule.invoke({
        "claimed_amount": claimed,
        "allowed_total": allowed,
        "decision_type": decision_type
    })

    citations = format_legal_citations.invoke({
        "policy_clauses": state.get("policy_clauses", []),
        "precedent_cases": state.get("precedent_cases", [])
    })

    rationale = (
        f"Based on automated multi-agent analysis for Claim {claim_id}: "
        f"The claim has been assigned a status of {decision_type}. "
        f"Approved payout: ${payout_info['approved_payout']}. "
        f"Key resolution notes: {state.get('conflict_resolution', 'Standard policy interpretation applied.')}"
    )

    draft = {
        "claim_id": claim_id,
        "decision_type": decision_type,
        "approved_amount": payout_info["approved_payout"],
        "rationale": rationale,
        "citations": citations,
        "itemized_payout": payout_info
    }

    return {
        "draft_decision": draft,
        "decision_type": decision_type,
        "approved_amount": payout_info["approved_payout"],
        "rationale": rationale,
        "citations": citations,
        "itemized_payout": payout_info,
        "last_completed_agent": "decision_drafting",
        "status": "DECISION_DRAFTED"
    }
