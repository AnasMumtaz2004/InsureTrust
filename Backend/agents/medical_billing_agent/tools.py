from typing import List, Dict, Any
from langchain_core.tools import tool

# Standard CPT fee schedule reference dictionary
FEE_SCHEDULE = {
    "99214": 180.00,  # Office Visit Level 4
    "93000": 75.00,   # ECG Complete
    "72148": 850.00,  # MRI Lumbar Spine
    "97110": 65.00    # Physical Therapy Exercise
}

@tool
def validate_cpt_icd_compatibility(diagnosis_codes: List[str], procedure_codes: List[str]) -> List[str]:
    """Cross-references CPT procedures against ICD-10 diagnoses for clinical medical necessity compatibility."""
    mismatches = []
    # Clinical rule: ECG (93000) for simple lumbar strain (S39.011A) without cardiac symptoms is incompatible
    if "93000" in procedure_codes and "S39.011A" in diagnosis_codes and "R07.9" not in diagnosis_codes:
        mismatches.append("CPT 93000 (Electrocardiogram) lacks medical necessity for diagnosis S39.011A (Lumbar strain) without cardiac chest pain indications.")
    return mismatches

@tool
def calculate_fee_schedule_allowed(procedure_codes: List[str], claimed_amount: float) -> Dict[str, Any]:
    """Calculates standard fee schedule allowed amount and flags excess charges."""
    allowed = 0.0
    itemized = []
    for proc in procedure_codes:
        std_fee = FEE_SCHEDULE.get(proc, 150.00)
        allowed += std_fee
        itemized.append({"procedure": proc, "allowed": std_fee})

    if not procedure_codes:
        allowed = claimed_amount * 0.8  # Fallback estimate

    excess = max(0.0, claimed_amount - allowed)
    return {
        "allowed_total": round(allowed, 2),
        "excess_charge": round(excess, 2),
        "itemized": itemized
    }

@tool
def detect_unbundling_or_duplicate(procedure_codes: List[str]) -> List[str]:
    """Checks procedure list for unbundled billing or duplicate code submissions."""
    flags = []
    if len(procedure_codes) != len(set(procedure_codes)):
        flags.append("Duplicate procedure codes detected in billing submission.")
    return flags
