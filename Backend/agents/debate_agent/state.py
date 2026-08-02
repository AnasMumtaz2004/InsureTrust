from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DebateState(BaseModel):
    """Slice of shared state managed by Debate/Reconciliation Agent."""
    pro_arguments: List[str] = []
    con_arguments: List[str] = []
    conflict_resolution: str = ""
    reconciliation_recommendation: str = ""  # "APPROVE", "DENY", "PARTIAL_APPROVE"
    confidence_delta: float = 0.0
    debate_transcript: Optional[Dict[str, Any]] = None
