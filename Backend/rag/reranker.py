from typing import List, Dict, Any

from config import settings

class TermOverlapReranker:
    """Fallback post-retrieval reranking based on keyword overlap."""
    
    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
        query_words = set(query.lower().split())
        scored = []

        for doc in documents:
            content = str(doc.get("content", "")).lower() + " " + str(doc.get("clause_title", "")).lower()
            doc_words = set(content.split())
            overlap = len(query_words.intersection(doc_words))
            base_score = 0.5 + (0.1 * overlap)
            scored.append((base_score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored[:top_k]]

class CrossEncoderReranker:
    """Post-retrieval reranking component to refine vector search results based on keyword overlap and semantic density."""
    def __init__(self):
        self.model_name = settings.reranker.model
        self.model = None
        self.fallback = TermOverlapReranker()
        if self.model_name:
            try:
                from sentence_transformers import CrossEncoder
                self.model = CrossEncoder(self.model_name)
            except Exception:
                pass  # fall back to TermOverlapReranker

    def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.model:
            return self.fallback.rerank(query, documents, top_k)
            
        pairs = [[query, str(doc.get("content", "")) + " " + str(doc.get("clause_title", ""))] for doc in documents]
        scores = self.model.predict(pairs)
        
        scored = [(scores[i], documents[i]) for i in range(len(documents))]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored[:top_k]]
