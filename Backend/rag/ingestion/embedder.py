import hashlib
from typing import List
from config import settings
from utils.logger import logger


class EmbeddingModelWrapper:
    """Wrapper around vector embeddings (OpenAI / HuggingFace / hash-vector fallback for offline/test environments)."""

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embeddings.model
        self.device = settings.embeddings.device
        self.dim = 384
        self.embedder = None

        # Try HuggingFace first
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            self.embedder = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs={"device": self.device},
            )
            logger.info(f"HuggingFaceEmbeddings loaded: {self.model_name}")
            return
        except Exception as e:
            logger.warning(f"HuggingFaceEmbeddings not available ({e}); trying OpenAI.")

        # Try OpenAI embeddings
        if settings.GROQ_API_KEY or getattr(settings, "OPENAI_API_KEY", ""):
            try:
                from langchain_openai import OpenAIEmbeddings
                self.embedder = OpenAIEmbeddings()
                logger.info("OpenAIEmbeddings loaded as embedding backend.")
                return
            except Exception as e:
                logger.warning(f"OpenAIEmbeddings not available ({e}); using hash-vector fallback.")

        logger.warning(
            "No embedding backend available. Using deterministic hash-vector fallback. "
            "Retrieval quality will be reduced."
        )

    # ------------------------------------------------------------------
    # Hash-vector fallback (deterministic, not semantic)
    # ------------------------------------------------------------------

    def _pseudo_vector(self, text: str) -> List[float]:
        """Repeats 2-char slices of a SHA-256 hex digest to produce a dim-length float vector."""
        digest = hashlib.sha256(text.encode()).hexdigest()
        vec = []
        while len(vec) < self.dim:
            for i in range(0, len(digest) - 1, 2):
                vec.append(int(digest[i: i + 2], 16) / 255.0)
                if len(vec) >= self.dim:
                    break
        return vec[: self.dim]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Batched document embedding call."""
        if self.embedder is not None:
            return self.embedder.embed_documents(texts)
        return [self._pseudo_vector(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        """Single query embedding call."""
        if self.embedder is not None:
            return self.embedder.embed_query(text)
        return self._pseudo_vector(text)
