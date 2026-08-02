from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DecisionDraftingState(BaseModel):
    """Slice of shared state managed by Decision Drafting Agent."""
    draft_decision: Dict[str, Any] = {}
    decision_type: str = "PENDING"  # "APPROVE", "DENY", "PARTIAL_APPROVE"
    rationale: str = ""
    approved_amount: float = 0.0
    citations: List[str] = []
    itemized_payout: Dict[str, Any] = {}
