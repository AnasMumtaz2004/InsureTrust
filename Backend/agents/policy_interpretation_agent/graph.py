from typing import Dict, Any
from agents.policy_interpretation_agent.tools import retrieve_policy_clauses, check_exclusion_triggers

def policy_interpretation_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node execution function for Policy Interpretation Agent."""
    description = state.get("description", "")
    diagnoses = state.get("diagnosis_codes", [])
    product_line = state.get("product_line", "HEALTH")

    query = f"{description} {' '.join(diagnoses)}"
    clauses = retrieve_policy_clauses.invoke({
        "query": query,
        "product_line": product_line,
        "top_k": 3
    })

    exclusions = check_exclusion_triggers.invoke({
        "clauses": clauses,
        "diagnosis_codes": diagnoses
    })

    status = "EXCLUDED" if exclusions else "COVERED"

    return {
        "policy_clauses": clauses,
        "coverage_status": status,
        "exclusion_triggers": exclusions,
        "policy_interpretation_notes": f"Analyzed {len(clauses)} policy clauses via RAG infrastructure.",
        "last_completed_agent": "policy_interpretation",
        "status": "POLICY_INTERPRETED"
    }
