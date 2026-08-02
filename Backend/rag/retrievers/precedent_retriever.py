from typing import List, Dict, Any
from rag.vectorstore.precedent_store import PrecedentVectorStore
from rag.reranker import CrossEncoderReranker

class PrecedentRetriever:
    """LangChain-compatible Retriever wrapping PrecedentVectorStore for Precedent Agent."""

    def __init__(self, vectorstore: PrecedentVectorStore = None):
        self.vectorstore = vectorstore or PrecedentVectorStore()
        self.reranker = CrossEncoderReranker()

    def get_similar_precedents(self, query: str, diagnosis_code: str = None, top_k: int = 3) -> List[Dict[str, Any]]:
        raw_cases = self.vectorstore.similarity_search(query, k=top_k * 2, diagnosis_code=diagnosis_code)
        reranked_cases = self.reranker.rerank(query, raw_cases, top_k=top_k)
        return reranked_cases
