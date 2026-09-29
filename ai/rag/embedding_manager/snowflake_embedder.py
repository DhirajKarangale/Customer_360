from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ai.utils.llm_utils import get_snowflake_embedding

class EmbeddingManager:

    def __init__(self, model: str, dimension: int) -> None:
        self._model = model
        self._dimension = dimension
        self._call_count = 0

    def embed_text(self, text: str) -> list[float]:
        self._call_count += 1
        return get_snowflake_embedding(text, self._model, self._dimension)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(t) for t in texts]

    def close(self) -> None:
        pass
