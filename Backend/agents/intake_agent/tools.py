from typing import Dict, Any, List
from langchain_core.tools import tool

@tool
def validate_claim_fields(claim_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validates presence of essential claim fields (policy_number, claimed_amount, diagnosis_codes)."""
    required = ["policy_number", "claimed_amount", "incident_date"]
    missing = [f for f in required if not claim_data.get(f)]
    return {
        "is_complete": len(missing) == 0,
        "missing_fields": missing
    }

@tool
def calculate_severity_score(claimed_amount: float, num_diagnoses: int, num_procedures: int) -> float:
    """Calculates a numerical severity score from 1.0 to 10.0 based on amount and medical code density."""
    score = 1.0
    if claimed_amount > 10000:
        score += 4.0
    elif claimed_amount > 3000:
        score += 2.0

    score += min(3.0, num_diagnoses * 0.8)
    score += min(3.0, num_procedures * 0.7)
    return round(min(10.0, score), 2)
