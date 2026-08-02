from typing import List, Dict, Any
from langchain_core.tools import tool
from rag.retrievers.policy_retriever import PolicyRetriever

policy_retriever = PolicyRetriever()

@tool
def retrieve_policy_clauses(query: str, product_line: str = "HEALTH", top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieves matching policy clauses from agent-agnostic RAG policy retriever infrastructure."""
    return policy_retriever.get_relevant_policy_clauses(query=query, product_line=product_line, top_k=top_k)

@tool
def check_exclusion_triggers(clauses: List[Dict[str, Any]], diagnosis_codes: List[str]) -> List[str]:
    """Inspects retrieved policy clauses against diagnosis codes to identify exclusion triggers."""
    exclusions = []
    for clause in clauses:
        title = clause.get("clause_title", "").lower()
        content = clause.get("content", "").lower()
        if "pre-existing" in title or "exclusion" in title:
            exclusions.append(f"Potential exclusion under '{clause.get('clause_title')}': Pre-existing condition verification required.")
    return exclusions
