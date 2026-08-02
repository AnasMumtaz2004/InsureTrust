from pydantic import BaseModel, Field
from typing import List, Dict, Any

class MedicalBillingState(BaseModel):
    """Slice of shared state managed by Medical/Billing Agent."""
    diagnosis_codes: List[str] = []
    procedure_codes: List[str] = []
    claimed_amount: float = 0.0
    medical_findings: List[Dict[str, Any]] = []
    code_mismatches: List[str] = []
    unusual_charges: List[str] = []
    allowed_total: float = 0.0
    billing_status: str = "UNKNOWN"
