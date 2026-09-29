from __future__ import annotations
import json
import os
from typing import Any, Optional
import faiss
import numpy as np
from ai.rag.vector_manager.metadata_store import MetadataStore

class VectorStoreManager:
    _FAISS_INDEX_FILE = 'faiss.index'
    _METADATA_FILE = 'metadata.pkl'
    _REGISTRY_FILE = 'registry.json'

    def __init__(self, store_dir: str, dimension: int) -> None:
        self._store_dir = store_dir
        self._dimension = dimension
        self._index: Optional[faiss.IndexFlatIP] = None
        self._metadata = MetadataStore(os.path.join(store_dir, self._METADATA_FILE))
        self._registry: dict[str, dict[str, Any]] = {}

    def initialize(self) -> None:
        os.makedirs(self._store_dir, exist_ok=True)
        if not self._load_existing():
            self._index = faiss.IndexFlatIP(self._dimension)

    def save(self) -> None:
        os.makedirs(self._store_dir, exist_ok=True)
        faiss.write_index(self._index, os.path.join(self._store_dir, self._FAISS_INDEX_FILE))
        self._metadata.save()
        with open(os.path.join(self._store_dir, self._REGISTRY_FILE), 'w') as f:
            json.dump(self._registry, f, indent=2)

    def load(self) -> bool:
        return self._load_existing()

    def add_documents(self, embeddings: list[list[float]], chunks: list[dict[str, Any]], document_id: str) -> None:
        if not embeddings or not chunks:
            return
        vectors = np.array(embeddings, dtype=np.float32)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        vectors = vectors / norms
        start_index = self._metadata.count
        self._metadata.add_entries(chunks)
        self._index.add(vectors)
        self._registry[document_id] = {'start_index': start_index, 'num_chunks': len(chunks)}

    def similarity_search(self, query_embedding: list[float], top_k: int, score_threshold: float) -> list[dict[str, Any]]:
        if self._index is None or self._index.ntotal == 0:
            return []
        query = np.array([query_embedding], dtype=np.float32)
        norms = np.linalg.norm(query, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        query = query / norms
        k = min(top_k, self._index.ntotal)
        scores, indices = self._index.search(query, k)
        results: list[dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or score < score_threshold:
                continue
            entry = self._metadata.get_entry(int(idx))
            if entry is not None:
                result = dict(entry)
                result['score'] = float(score)
                results.append(result)
        return results

    def get_document_count(self) -> int:
        if self._index is None:
            return 0
        return self._index.ntotal

    def get_ingested_document_ids(self) -> set[str]:
        return set(self._registry.keys())

    def is_document_ingested(self, document_id: str) -> bool:
        return document_id in self._registry

    def _load_existing(self) -> bool:
        index_path = os.path.join(self._store_dir, self._FAISS_INDEX_FILE)
        registry_path = os.path.join(self._store_dir, self._REGISTRY_FILE)
        if not os.path.exists(index_path):
            return False
        try:
            self._index = faiss.read_index(index_path)
            self._metadata.load()
            if os.path.exists(registry_path):
                with open(registry_path, 'r') as f:
                    self._registry = json.load(f)
            return True
        except Exception as e:
            print(f'  [WARN] Failed to load existing vector store: {e}')
            self._index = None
            self._metadata = MetadataStore(os.path.join(self._store_dir, self._METADATA_FILE))
            self._registry = {}
            return False
