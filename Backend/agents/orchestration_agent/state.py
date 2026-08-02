from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class OrchestrationState(BaseModel):
    """Slice of shared state managed by Orchestration Agent."""
    # Reads
    complexity_score: float = 0.0
    is_complex: bool = False
    conflict_flags: List[str] = []
    agent_outputs_so_far: List[str] = []

    # Writes
    next_agent: str = "intake_agent"
    workflow_path: List[str] = []
    escalation_required: bool = False
    escalation_reason: Optional[str] = None
    workflow_reasoning: str = ""
