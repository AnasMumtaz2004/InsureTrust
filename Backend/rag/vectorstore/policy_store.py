from typing import List, Dict, Any
from rag.ingestion.embedder import EmbeddingModelWrapper
from utils.logger import logger

class PolicyVectorStore:
    """Vector store client managing policy clause indexing and similarity retrieval."""

    def __init__(self):
        self.embedder = EmbeddingModelWrapper()
        # In-memory document store fallback with similarity scoring
        self._documents: List[Dict[str, Any]] = []
        self._vectors: List[List[float]] = []

    def add_policy_clauses(self, chunks: List[Dict[str, Any]]):
        """Indexes policy clause chunks into the vector store."""
        for chunk in chunks:
            text = f"{chunk.get('clause_title', '')}: {chunk.get('content', '')}"
            vec = self.embedder.embed_query(text)
            self._documents.append(chunk)
            self._vectors.append(vec)
        logger.info(f"Indexed {len(chunks)} policy clause documents into PolicyVectorStore.")

    def similarity_search(self, query: str, k: int = 4, product_line: str = None) -> List[Dict[str, Any]]:
        """Retrieves top-k policy clauses matching query vector."""
        if not self._documents:
            # Seed default policy clauses if empty
            self._seed_default_clauses()

        query_vec = self.embedder.embed_query(query)
        scored_results = []

        for idx, doc in enumerate(self._documents):
            if product_line and doc.get("product_line") != product_line:
                continue
            doc_vec = self._vectors[idx]
            score = self._cosine_similarity(query_vec, doc_vec)
            scored_results.append((score, doc))

        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_results[:k]]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def _seed_default_clauses(self):
        sample_clauses = [
            {
                "id": "POL-GENERAL-EXCL-01",
                "policy_number": "STANDARD-HEALTH-01",
                "product_line": "HEALTH",
                "clause_title": "Pre-Existing Condition Exclusion Clause",
                "content": "Services rendered for medical conditions diagnosed prior to the 90-day waiting period from policy inception are excluded unless pre-authorization is granted.",
                "metadata": {"section": "EXCLUSIONS"}
            },
            {
                "id": "POL-GENERAL-COV-02",
                "policy_number": "STANDARD-HEALTH-01",
                "product_line": "HEALTH",
                "clause_title": "Outpatient Diagnostic Services Coverage",
                "content": "Outpatient laboratory and radiological diagnostic procedures are covered at 80% coinsurance after the annual deductible is met.",
                "metadata": {"section": "COVERAGE"}
            },
            {
                "id": "POL-AUTO-COLL-03",
                "policy_number": "STANDARD-AUTO-01",
                "product_line": "AUTO",
                "clause_title": "Collision and Third Party Property Damage",
                "content": "Covers physical repair costs resulting from vehicular collision up to the actual cash value of the vehicle subject to a $500 deductible.",
                "metadata": {"section": "COVERAGE"}
            }
        ]
        self.add_policy_clauses(sample_clauses)
