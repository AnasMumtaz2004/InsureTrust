from typing import Dict, Any
from agents.compliance_guardrail_agent.tools import check_statutory_mandates, evaluate_human_review_threshold

def compliance_guardrail_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node execution function for Compliance Guardrail Agent."""
    claimed = float(state.get("claimed_amount", 0.0))
    complexity = float(state.get("complexity_score", 0.0))
    draft = state.get("draft_decision", {})
    decision_type = draft.get("decision_type", state.get("decision_type", "PENDING"))
    rationale = draft.get("rationale", "")

    # Step 1: Statutory legal mandate checks
    statutory_flags = check_statutory_mandates.invoke({
        "decision_type": decision_type,
        "rationale": rationale
    })

    # Step 2: Human-in-the-loop threshold checks
    threshold_eval = evaluate_human_review_threshold.invoke({
        "claimed_amount": claimed,
        "complexity_score": complexity,
        "decision_type": decision_type
    })

    requires_human = threshold_eval["requires_human"]
    all_flags = statutory_flags + threshold_eval["reasons"]
    compliance_passed = len(statutory_flags) == 0

    final_decision = dict(draft)
    final_decision["compliance_passed"] = compliance_passed
    final_decision["compliance_flags"] = all_flags
    final_decision["requires_human_approval"] = requires_human

    status = "PAUSED_FOR_HUMAN_REVIEW" if requires_human else "COMPLIANCE_PASSED"

    return {
        "compliance_passed": compliance_passed,
        "compliance_flags": all_flags,
        "human_review_required": requires_human,
        "human_review_reason": "; ".join(threshold_eval["reasons"]) if requires_human else None,
        "final_decision": final_decision,
        "last_completed_agent": "compliance_guardrail",
        "status": status
    }
