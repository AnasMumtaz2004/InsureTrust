from pydantic import BaseModel, Field
from typing import List, Dict, Any

class PolicyInterpretationState(BaseModel):
    """Slice of shared state managed by Policy Interpretation Agent."""
    policy_number: str
    product_line: str = "HEALTH"
    extracted_clauses: List[Dict[str, Any]] = []
    coverage_status: str = "UNKNOWN"  # "COVERED", "EXCLUDED", "CONDITIONALLY_COVERED"
    policy_interpretation_notes: str = ""
    exclusion_triggers: List[str] = []
