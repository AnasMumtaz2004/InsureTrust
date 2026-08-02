from pydantic import BaseModel, Field
from typing import List, Dict, Any

class PrecedentState(BaseModel):
    """Slice of shared state managed by Precedent Agent."""
    diagnosis_codes: List[str] = []
    procedure_codes: List[str] = []
    description: str = ""
    precedent_cases: List[Dict[str, Any]] = []
    historical_approval_rate: float = 0.0
    precedent_summary: str = ""
    key_distinctions: List[str] = []
