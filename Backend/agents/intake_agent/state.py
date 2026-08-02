from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class IntakeState(BaseModel):
    """Slice of shared state managed by Intake Agent."""
    claim_id: str
    policy_number: str
    claimed_amount: float
    diagnosis_codes: List[str] = []
    procedure_codes: List[str] = []
    description: str = ""
    is_complete: bool = False
    missing_fields: List[str] = []
    complexity_score: float = 0.0
    is_complex: bool = False
