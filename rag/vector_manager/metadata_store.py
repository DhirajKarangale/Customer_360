from __future__ import annotations

import os
import pickle
from typing import Any, Optional


class MetadataStore:
    """Persists chunk text and metadata alongside FAISS indices using pickle."""

    def __init__(self, store_path: str) -> None:
        self._store_path = store_path
        self._entries: list[dict[str, Any]] = []

    def add_entry(self, entry: dict[str, Any]) -> int:
        """Add a single entry. Returns its index."""
        index = len(self._entries)
        self._entries.append(entry)
        return index

    def add_entries(self, entries: list[dict[str, Any]]) -> list[int]:
        """Add multiple entries. Returns their indices."""
        start = len(self._entries)
        self._entries.extend(entries)
        return list(range(start, start + len(entries)))

    def get_entry(self, index: int) -> Optional[dict[str, Any]]:
        """Retrieve entry by FAISS index position."""
        if 0 <= index < len(self._entries):
            return self._entries[index]
        return None

    def get_entries(self, indices: list[int]) -> list[Optional[dict[str, Any]]]:
        """Retrieve multiple entries by index positions."""
        return [self.get_entry(i) for i in indices]

    @property
    def count(self) -> int:
        return len(self._entries)

    def save(self) -> None:
        os.makedirs(os.path.dirname(self._store_path), exist_ok=True)
        with open(self._store_path, "wb") as f:
            pickle.dump(self._entries, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load(self) -> bool:
        """Load from disk. Returns True if loaded successfully."""
        if not os.path.exists(self._store_path):
            return False
        with open(self._store_path, "rb") as f:
            self._entries = pickle.load(f)
        return True
