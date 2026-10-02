from typing import Dict, Any, List
from langchain_core.tools import tool
from config import settings

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
    score = settings.severity.base
    if claimed_amount > settings.severity.amount_high:
        score += settings.severity.amount_high_points
    elif claimed_amount > settings.severity.amount_mid:
        score += settings.severity.amount_mid_points

    score += min(settings.severity.diagnosis_cap, num_diagnoses * settings.severity.per_diagnosis)
    score += min(settings.severity.procedure_cap, num_procedures * settings.severity.per_procedure)
    return round(min(10.0, score), 2)
