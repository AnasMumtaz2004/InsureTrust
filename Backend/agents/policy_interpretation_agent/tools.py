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
    """Inspects clause language and diagnosis data to identify exclusion triggers."""
    exclusions = []
    exclusion_keywords = (
        "pre-existing",
        "preexisting",
        "waiting period",
        "excluded",
        "exclusion",
        "not covered",
        "no coverage",
        "not eligible",
        "specific exclusion",
        "not payable",
    )
    diagnosis_tokens = [str(code).lower() for code in diagnosis_codes if code]

    for clause in clauses:
        title = str(clause.get("clause_title", "")).lower()
        content = str(clause.get("content", "")).lower()
        combined = f"{title} {content}".strip()
        if not combined or not diagnosis_tokens:
            continue

        keyword_match = any(keyword in combined for keyword in exclusion_keywords)
        diagnosis_match = any(code in combined for code in diagnosis_tokens)

        if keyword_match and diagnosis_match:
            exclusions.append(
                f"Potential exclusion under '{clause.get('clause_title', 'Policy clause')}': "
                "Pre-existing condition or exclusion language requires verification."
            )

    return exclusions
