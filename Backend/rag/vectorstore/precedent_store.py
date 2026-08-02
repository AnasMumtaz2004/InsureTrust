from typing import List, Dict, Any
from rag.ingestion.embedder import EmbeddingModelWrapper
from utils.logger import logger

class PrecedentVectorStore:
    """Vector store manager for historical precedent claims and adjudication outcomes."""

    def __init__(self):
        self.embedder = EmbeddingModelWrapper()
        self._documents: List[Dict[str, Any]] = []
        self._vectors: List[List[float]] = []

    def add_precedent_records(self, records: List[Dict[str, Any]]):
        for rec in records:
            text = f"{rec.get('precedent_code', '')}: {rec.get('content', '')}"
            vec = self.embedder.embed_query(text)
            self._documents.append(rec)
            self._vectors.append(vec)
        logger.info(f"Indexed {len(records)} precedent records into PrecedentVectorStore.")

    def similarity_search(self, query: str, k: int = 3, diagnosis_code: str = None) -> List[Dict[str, Any]]:
        if not self._documents:
            self._seed_default_precedents()

        query_vec = self.embedder.embed_query(query)
        scored = []

        for idx, doc in enumerate(self._documents):
            meta = doc.get("metadata", {})
            score = self._cosine_similarity(query_vec, self._vectors[idx])
            # Boost score if diagnosis code matches exactly
            if diagnosis_code and meta.get("diagnosis_code") == diagnosis_code:
                score += 0.2
            scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored[:k]]

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def _seed_default_precedents(self):
        sample_precedents = [
            {
                "id": "PREC-2025-0892",
                "precedent_code": "PREC-2025-0892",
                "content": "Diagnosis M54.5 (Lumbago), Procedure 99214. Patient had 6 sessions of physical therapy. Claim approved after verifying prior authorization on file.",
                "metadata": {"diagnosis_code": "M54.5", "procedure_code": "99214", "decision_outcome": "APPROVED"}
            },
            {
                "id": "PREC-2025-0411",
                "precedent_code": "PREC-2025-0411",
                "content": "Diagnosis S39.011A (Lumbar strain), Procedure 93000 (ECG). Claim denied for ECG as procedure was deemed not medically necessary for routine back strain without cardiac symptoms.",
                "metadata": {"diagnosis_code": "S39.011A", "procedure_code": "93000", "decision_outcome": "DENIED"}
            },
            {
                "id": "PREC-2024-1105",
                "precedent_code": "PREC-2024-1105",
                "content": "High-value lumbar MRI without conservative therapy trial. Partial approval granted for physical therapy, MRI payment deferred pending clinical records.",
                "metadata": {"diagnosis_code": "M54.5", "procedure_code": "72148", "decision_outcome": "PARTIAL_APPROVE"}
            }
        ]
        self.add_precedent_records(sample_precedents)
