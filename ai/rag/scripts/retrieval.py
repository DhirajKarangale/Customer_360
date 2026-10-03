import os
import re
import sys
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)
from ai.rag.config import (
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL,
    SIMILARITY_SCORE_THRESHOLD,
    TOP_K,
    VECTOR_STORE_DIR,
)
from ai.rag.pipeline.snowflake_embedder import EmbeddingManager
from ai.rag.pipeline.faiss_store import VectorStoreManager
from ai.utils.message_manager import get_message
class RAGRetrievalPipeline:
    def __init__(self):
        self._embedder = EmbeddingManager(EMBEDDING_MODEL, EMBEDDING_DIMENSION)
        self._vector_store = VectorStoreManager(VECTOR_STORE_DIR, EMBEDDING_DIMENSION)
        self._vector_store.initialize()
    def close(self):
        self._embedder.close()