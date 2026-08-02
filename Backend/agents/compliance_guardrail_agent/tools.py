from typing import List, Dict, Any
from langchain_core.tools import tool
from config import settings

@tool
def check_statutory_mandates(decision_type: str, rationale: str) -> List[str]:
    """Verifies that denial rationale contains required statutory legal appeals notice text."""
    flags = []
    if decision_type in ["DENY", "PARTIAL_APPROVE"] and "right to request" not in rationale.lower():
        flags.append("Statutory Mandate Warning: Decision rationale must include consumer right-to-appeal notice.")
    return flags

@tool
def evaluate_human_review_threshold(claimed_amount: float, complexity_score: float, decision_type: str) -> Dict[str, Any]:
    """Evaluates whether financial amount or complexity triggers mandatory human-in-the-loop adjudicator review."""
    requires_human = False
    reasons = []

    if claimed_amount >= settings.AUTO_APPROVAL_MAX_AMOUNT:
        requires_human = True
        reasons.append(f"Claim amount ${claimed_amount:,.2f} exceeds auto-approval threshold (${settings.AUTO_APPROVAL_MAX_AMOUNT:,.2f}).")

    if complexity_score >= settings.HIGH_COMPLEXITY_SCORE_THRESHOLD:
        requires_human = True
        reasons.append(f"Complexity score {complexity_score} exceeds human review threshold ({settings.HIGH_COMPLEXITY_SCORE_THRESHOLD}).")

    if decision_type == "DENY":
        requires_human = True
        reasons.append("Adversarial denial decisions require mandatory human adjudicator validation.")

    return {
        "requires_human": requires_human,
        "reasons": reasons
    }
