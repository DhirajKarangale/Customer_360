from __future__ import annotations
from typing import Any


class ChunkManager:

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError('chunk_overlap must be less than chunk_size')
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    def chunk_document(self, content: str, metadata: dict[str, Any]) -> list[dict[str, Any]]:
        if not content or not content.strip():
            return []
        content = content.strip()
        if len(content) <= self._chunk_size:
            return [{'chunk_text': content, 'chunk_index': 0, 'total_chunks': 1, 'metadata': metadata}]
        raw_chunks = self._split_text(content)
        total = len(raw_chunks)
        return [{'chunk_text': chunk, 'chunk_index': i, 'total_chunks': total, 'metadata': metadata} for i, chunk in enumerate(raw_chunks)]

    def _split_text(self, text: str) -> list[str]:
        chunks: list[str] = []
        step = self._chunk_size - self._chunk_overlap
        start = 0
        text_len = len(text)
        while start < text_len:
            end = min(start + self._chunk_size, text_len)
            if end < text_len:
                boundary = text.rfind(' ', start, end)
                if boundary > start:
                    end = boundary
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= text_len:
                break
            start += step
        return chunks
