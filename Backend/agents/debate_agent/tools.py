from typing import List, Dict, Any
from langchain_core.tools import tool
from config import settings

@tool
def evaluate_argument_strength(arguments: List[str], evidence_count: int) -> float:
    """Evaluates numerical strength score (0.0 to 1.0) of argument list based on supporting evidence count."""
    if not arguments:
        return settings.debate.per_evidence
    base = min(settings.debate.cap, settings.debate.base + (len(arguments) * settings.debate.per_argument) + (evidence_count * settings.debate.per_evidence))
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
