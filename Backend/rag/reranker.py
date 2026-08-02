from typing import List, Dict, Any

class CrossEncoderReranker:
    """Post-retrieval reranking component to refine vector search results based on keyword overlap and semantic density."""

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
