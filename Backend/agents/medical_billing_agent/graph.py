from typing import Dict, Any
from agents.medical_billing_agent.tools import (
    validate_cpt_icd_compatibility,
    calculate_fee_schedule_allowed,
    detect_unbundling_or_duplicate
)

def medical_billing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node execution function for Medical/Billing Agent."""
    diagnoses = state.get("diagnosis_codes", [])
    procedures = state.get("procedure_codes", [])
    claimed = float(state.get("claimed_amount", 0.0))

    # Audit step 1: CPT/ICD compatibility
    mismatches = validate_cpt_icd_compatibility.invoke({
        "diagnosis_codes": diagnoses,
        "procedure_codes": procedures
    })

    # Audit step 2: Fee schedule calculations
    fee_calc = calculate_fee_schedule_allowed.invoke({
        "procedure_codes": procedures,
        "claimed_amount": claimed
    })

    # Audit step 3: Unbundling check
    unbundling_flags = detect_unbundling_or_duplicate.invoke({
        "procedure_codes": procedures
    })

    medical_findings = [
        {"type": "fee_schedule", "details": fee_calc},
        {"type": "mismatches", "details": mismatches},
        {"type": "unbundling", "details": unbundling_flags}
    ]

    billing_status = "MISMATCH_FLAGGED" if mismatches or unbundling_flags else "VERIFIED"

    return {
        "medical_findings": medical_findings,
        "code_mismatches": mismatches,
        "unusual_charges": unbundling_flags,
        "allowed_total": fee_calc["allowed_total"],
        "billing_status": billing_status,
        "last_completed_agent": "medical_billing",
        "status": "MEDICAL_BILLED"
    }
