from typing import Dict, Any
from agents.intake_agent.tools import validate_claim_fields, calculate_severity_score
from config import settings

def intake_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node execution function for Intake & Classification Agent."""
    claim_id = state.get("claim_id", "UNKNOWN")
    claimed_amount = float(state.get("claimed_amount", 0.0))
    diagnoses = state.get("diagnosis_codes", [])
    procedures = state.get("procedure_codes", [])

    # Step 1: Validate required fields
    validation = validate_claim_fields.invoke({"claim_data": state})
    is_complete = validation["is_complete"]
    missing = validation["missing_fields"]

    # Step 2: Compute severity and complexity
    severity = calculate_severity_score.invoke({
        "claimed_amount": claimed_amount,
        "num_diagnoses": len(diagnoses),
        "num_procedures": len(procedures)
    })

    is_complex = severity >= settings.HIGH_COMPLEXITY_SCORE_THRESHOLD or claimed_amount >= settings.AUTO_APPROVAL_MAX_AMOUNT

    return {
        "is_complete": is_complete,
        "missing_fields": missing,
        "complexity_score": severity,
        "is_complex": is_complex,
        "last_completed_agent": "intake_agent",
        "status": "INTAKE_CLASSIFIED"
    }
