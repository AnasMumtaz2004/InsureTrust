from typing import List, Dict, Any
from langchain_core.tools import tool

@tool
def evaluate_argument_strength(arguments: List[str], evidence_count: int) -> float:
    """Evaluates numerical strength score (0.0 to 1.0) of argument list based on supporting evidence count."""
    if not arguments:
        return 0.10
    base = min(0.95, 0.40 + (len(arguments) * 0.15) + (evidence_count * 0.10))
    return round(base, 2)

@tool
def summarize_debate_transcript(pro_args: List[str], con_args: List[str], resolution: str) -> Dict[str, Any]:
    """Formats structured debate transcript artifact for audit trail logging."""
    return {
        "pro_approval_view": pro_args,
        "pro_denial_view": con_args,
        "synthesis": resolution,
        "debate_rounds": 1
    }
