from typing import List, Dict, Any
from langchain_core.tools import tool
from rag.retrievers.precedent_retriever import PrecedentRetriever

precedent_retriever = PrecedentRetriever()

@tool
def retrieve_similar_precedents(query: str, diagnosis_code: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieves similar past adjudicated claims from RAG precedent store."""
    return precedent_retriever.get_similar_precedents(query=query, diagnosis_code=diagnosis_code, top_k=top_k)

@tool
def calculate_historical_approval_rate(precedent_cases: List[Dict[str, Any]]) -> float:
    """Calculates approval percentage across retrieved historical cases."""
    if not precedent_cases:
        return 0.50
    approved_count = 0
    for case in precedent_cases:
        meta = case.get("metadata", {})
        outcome = meta.get("decision_outcome", "").upper()
        if "APPROV" in outcome:
            approved_count += 1
    return round(approved_count / len(precedent_cases), 2)
