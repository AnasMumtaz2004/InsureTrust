from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ComplianceState(BaseModel):
    """Slice of shared state managed by Compliance Guardrail Agent."""
    compliance_passed: bool = True
    compliance_flags: List[str] = []
    human_review_required: bool = False
    human_review_reason: Optional[str] = None
    final_decision: Optional[Dict[str, Any]] = None
