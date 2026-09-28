from __future__ import annotations

from typing import Any, Optional

from rag.config import (
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL,
    SIMILARITY_SCORE_THRESHOLD,
    TOP_K,
    VECTOR_STORE_DIR,
)
from rag.embedding_manager import EmbeddingManager
from rag.vector_manager import VectorStoreManager


class RetrievalPipeline:
    """Handles RAG retrieval: query → embed → search → return ranked results."""

    def __init__(self, store_dir: Optional[str] = None) -> None:
        self._embedder = EmbeddingManager(EMBEDDING_MODEL, EMBEDDING_DIMENSION)
        self._vector_store = VectorStoreManager(
            store_dir or VECTOR_STORE_DIR, EMBEDDING_DIMENSION
        )
        self._vector_store.initialize()

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ) -> list[dict[str, Any]]:
        """
        Embed the query and search for most similar chunks.
        Returns list of chunk dicts with 'score', 'chunk_text', 'metadata', etc.
        """
        query_embedding = self._embedder.embed_text(query)
        return self._vector_store.similarity_search(
            query_embedding,
            top_k=top_k if top_k is not None else TOP_K,
            score_threshold=score_threshold if score_threshold is not None else SIMILARITY_SCORE_THRESHOLD,
        )

    def close(self) -> None:
        """Release resources."""
        self._embedder.close()
