from typing import List
from config import settings
from utils.logger import logger

class EmbeddingModelWrapper:
    """Wrapper around vector embeddings (OpenAI / Mock fallback for offline/test environments)."""

    def __init__(self, model_name: str = settings.DEFAULT_EMBEDDING_MODEL):
        self.model_name = model_name
        self.dim = 1536 if "3-small" in model_name or "ada" in model_name else 384

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Batched document embedding call."""
        if settings.OPENAI_API_KEY:
            try:
                from langchain_community.embeddings import OpenAIEmbeddings
                embedder = OpenAIEmbeddings(model=self.model_name, openai_api_key=settings.OPENAI_API_KEY)
                return embedder.embed_documents(texts)
            except Exception as e:
                logger.warning(f"Failed to call OpenAI Embeddings API: {e}. Falling back to deterministic mock vectors.")

        # Fallback deterministic pseudo-vector generator for local testing without API keys
        return [self._pseudo_vector(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        """Single query embedding call."""
        return self.embed_documents([text])[0]

    def _pseudo_vector(self, text: str) -> List[float]:
        import hashlib
        h = hashlib.sha256(text.encode('utf-8')).hexdigest()
        vec = []
        for i in range(self.dim):
            sub = h[(i * 2) % len(h): ((i * 2) % len(h)) + 2]
            val = (int(sub, 16) / 255.0) - 0.5
            vec.append(val)
        return vec
