from typing import List, Dict, Any
from langchain_core.tools import tool
from config import settings

@tool
def evaluate_claim_complexity(claimed_amount: float, severity_score: float) -> Dict[str, Any]:
    """Evaluates whether claim requires complex multi-agent analysis or simple fast-tracking."""
    is_complex = (
        claimed_amount >= settings.AUTO_APPROVAL_MAX_AMOUNT or
        severity_score >= settings.HIGH_COMPLEXITY_SCORE_THRESHOLD
    )
    return {
        "is_complex": is_complex,
        "complexity_score": severity_score
    }

@tool
def detect_conflict(
    coverage_status: str,
    code_mismatches: List[str],
    exclusion_triggers: List[str] | None = None,
    unusual_charges: List[str] | None = None,
) -> List[str]:
    """Detects conflicts between policy coverage status and medical/billing findings."""
    conflicts = []
    if str(coverage_status).upper() == "EXCLUDED":
        conflicts.append("Policy interpretation flagged EXCLUDED coverage status.")
    if code_mismatches:
        conflicts.extend([f"Medical billing code mismatch: {m}" for m in code_mismatches])
    if unusual_charges:
        conflicts.extend([f"Unusual charge pattern: {u}" for u in unusual_charges])
    return conflicts

@tool
def assess_escalation_need(claimed_amount: float, complexity_score: float, human_review_required: bool) -> Dict[str, Any]:
    """Assesses whether claim requires escalation to back-office human adjudicator."""
    reasons = []
    if claimed_amount >= settings.AUTO_APPROVAL_MAX_AMOUNT:
        reasons.append(f"Claim amount (${claimed_amount:,.2f}) exceeds auto-approval threshold.")
    if complexity_score >= settings.HIGH_COMPLEXITY_SCORE_THRESHOLD:
        reasons.append(f"Complexity score ({complexity_score}) exceeds threshold.")
    if human_review_required:
        reasons.append("Worker agent requested human review.")

    return {
        "escalation_required": len(reasons) > 0,
        "reasons": reasons
    }

@tool
def determine_next_agent(
    last_completed_agent: str,
    is_complex: bool,
    conflicts: List[str],
    human_review_required: bool
) -> Dict[str, Any]:
    """Determines the single authoritative next worker agent in the workflow sequence."""
    if not last_completed_agent or last_completed_agent == "START":
        next_agent = "intake_agent"
        reasoning = "Workflow initialized -> routed to Intake Agent."
    elif last_completed_agent == "intake_agent":
        next_agent = "policy_interpretation"
        reasoning = "Intake completed -> routed to Policy Interpretation Agent."
    elif last_completed_agent == "policy_interpretation":
        next_agent = "medical_billing"
        reasoning = "Policy Interpretation completed -> routed to Medical Billing Agent."
    elif last_completed_agent == "medical_billing":
        next_agent = "precedent_agent"
        reasoning = "Medical Billing audit completed -> routed to Precedent Agent."
    elif last_completed_agent == "precedent_agent":
        if conflicts:
            next_agent = "debate_agent"
            reasoning = "Policy Agent and Medical Agent outputs conflicted -> routed to Debate Agent."
        else:
            next_agent = "decision_drafting"
            reasoning = "Precedent retrieval completed with no conflicts -> routed to Decision Drafting Agent."
    elif last_completed_agent == "debate_agent":
        next_agent = "decision_drafting"
        reasoning = "Debate reconciliation completed -> routed to Decision Drafting Agent."
    elif last_completed_agent == "decision_drafting":
        next_agent = "compliance_guardrail"
        reasoning = "Decision Drafting completed -> routed to Compliance Guardrail Agent."
    elif last_completed_agent == "compliance_guardrail":
        if human_review_required:
            next_agent = "human_review_interrupt"
            reasoning = "Compliance audit flagged escalation requirements -> routed to Human Review Interrupt."
        else:
            next_agent = "finalize_decision"
            reasoning = "Compliance audit passed -> routed to Finalize Decision."
    elif last_completed_agent == "human_review_interrupt":
        next_agent = "finalize_decision"
        reasoning = "Human review completed -> routed to Finalize Decision."
    else:
        next_agent = "finalize_decision"
        reasoning = "Workflow execution completed."

    return {
        "next_agent": next_agent,
        "workflow_reasoning": reasoning
    }
