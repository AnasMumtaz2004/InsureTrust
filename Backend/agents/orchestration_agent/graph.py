from typing import Dict, Any
from agents.orchestration_agent.tools import (
    evaluate_claim_complexity,
    detect_conflict,
    assess_escalation_need,
    determine_next_agent
)

def orchestration_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node execution function for Orchestration Agent (the single routing authority)."""
    last_completed = state.get("last_completed_agent", "START")
    claimed = float(state.get("claimed_amount", 0.0))
    severity = float(state.get("complexity_score", 0.0))
    coverage_status = state.get("coverage_status", "")
    code_mismatches = state.get("code_mismatches", [])
    exclusion_triggers = state.get("exclusion_triggers", [])
    human_review_required = state.get("human_review_required", False)

    # 1. Complexity evaluation
    comp_eval = evaluate_claim_complexity.invoke({"claimed_amount": claimed, "severity_score": severity})

    # 2. Conflict detection
    conflicts = detect_conflict.invoke({
        "coverage_status": coverage_status,
        "code_mismatches": code_mismatches,
        "exclusion_triggers": exclusion_triggers
    })

    # 3. Escalation assessment
    esc_eval = assess_escalation_need.invoke({
        "claimed_amount": claimed,
        "complexity_score": comp_eval["complexity_score"],
        "human_review_required": human_review_required
    })

    # 4. Next agent decision
    next_step = determine_next_agent.invoke({
        "last_completed_agent": last_completed,
        "is_complex": comp_eval["is_complex"],
        "conflicts": conflicts,
        "human_review_required": esc_eval["escalation_required"]
    })

    workflow_path = state.get("workflow_path", [])
    if last_completed not in workflow_path and last_completed != "START":
        workflow_path.append(last_completed)

    return {
        "is_complex": comp_eval["is_complex"],
        "conflict_flags": conflicts,
        "escalation_required": esc_eval["escalation_required"],
        "escalation_reason": "; ".join(esc_eval["reasons"]) if esc_eval["escalation_required"] else None,
        "next_agent": next_step["next_agent"],
        "workflow_reasoning": next_step["workflow_reasoning"],
        "workflow_path": workflow_path,
        "status": f"ORCHESTRATED_TO_{next_step['next_agent'].upper()}"
    }

def route_next_agent(state: Dict[str, Any]) -> str:
    """Authoritative routing function used by main_graph.py conditional edges."""
    return state.get("next_agent", "intake_agent")
