from __future__ import annotations
from ai.utils.llm_utils import get_snowflake_embedding
import sys
import os
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
class EmbeddingManager:
    def __init__(self, model: str, dimension: int) -> None:
        self._model = model
        self._dimension = dimension
    def embed_text(self, text: str) -> list[float]:
        return get_snowflake_embedding(text, self._model, self._dimension)

    def close(self) -> None:
        pass