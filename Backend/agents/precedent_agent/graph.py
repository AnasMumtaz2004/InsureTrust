from typing import Dict, Any
from agents.precedent_agent.tools import retrieve_similar_precedents, calculate_historical_approval_rate

def precedent_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node execution function for Precedent Agent."""
    description = state.get("description", "")
    diagnoses = state.get("diagnosis_codes", [])
    primary_diag = diagnoses[0] if diagnoses else None

    query = f"{description} {' '.join(diagnoses)}"
    cases = retrieve_similar_precedents.invoke({
        "query": query,
        "diagnosis_code": primary_diag,
        "top_k": 3
    })

    rate = calculate_historical_approval_rate.invoke({
        "precedent_cases": cases
    })

    return {
        "precedent_cases": cases,
        "historical_approval_rate": rate,
        "precedent_summary": f"Retrieved {len(cases)} precedent cases with {int(rate*100)}% historical approval consensus.",
        "last_completed_agent": "precedent_agent",
        "status": "PRECEDENT_RETRIEVED"
    }
