from typing import List, Dict, Any
from langchain_core.tools import tool

@tool
def format_legal_citations(policy_clauses: List[Dict[str, Any]], precedent_cases: List[Dict[str, Any]]) -> List[str]:
    """Formats explicit policy clause and historical precedent citations for the decision letter."""
    citations = []
    for clause in policy_clauses:
        title = clause.get("clause_title", "Policy Clause")
        pid = clause.get("id", "POL-REF")
        citations.append(f"Policy Clause Ref [{pid}]: {title}")

    for prec in precedent_cases:
        pcode = prec.get("precedent_code", "PREC-REF")
        citations.append(f"Historical Precedent Ref [{pcode}]: Outcome {prec.get('metadata', {}).get('decision_outcome', 'Adjudicated')}")

    return citations

@tool
def compute_final_payout_schedule(claimed_amount: float, allowed_total: float, decision_type: str) -> Dict[str, Any]:
    """Calculates final payout schedule, deductible deductions, and approved total."""
    if decision_type == "DENY":
        payout = 0.0
    elif decision_type == "APPROVE":
        payout = min(claimed_amount, allowed_total if allowed_total > 0 else claimed_amount)
    else:
        payout = allowed_total

    return {
        "claimed_amount": claimed_amount,
        "approved_payout": round(payout, 2),
        "deductions": round(max(0.0, claimed_amount - payout), 2)
    }
