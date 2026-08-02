from typing import List, Dict, Any
from rag.vectorstore.policy_store import PolicyVectorStore
from rag.reranker import CrossEncoderReranker

class PolicyRetriever:
    """LangChain-compatible Retriever wrapping PolicyVectorStore for Policy Interpretation Agent."""

    def __init__(self, vectorstore: PolicyVectorStore = None):
        self.vectorstore = vectorstore or PolicyVectorStore()
        self.reranker = CrossEncoderReranker()

    def get_relevant_policy_clauses(self, query: str, product_line: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
        raw_docs = self.vectorstore.similarity_search(query, k=top_k * 2, product_line=product_line)
        reranked_docs = self.reranker.rerank(query, raw_docs, top_k=top_k)
        return reranked_docs
