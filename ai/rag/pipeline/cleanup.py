from __future__ import annotations
import os
import shutil
from typing import Optional
from ai.rag.config import CHUNKS_DATA_DIR, EMBEDDINGS_DATA_DIR, VECTOR_STORE_DIR
import logging
logger = logging.getLogger(__name__)
class CleanupManager:
    @staticmethod
    def cleanup_chunks(chunks_dir: Optional[str] = None) -> None:
        target = chunks_dir or CHUNKS_DATA_DIR
        CleanupManager._remove_directory(target, "chunks")
    @staticmethod
    def cleanup_embeddings(embeddings_dir: Optional[str] = None) -> None:
        target = embeddings_dir or EMBEDDINGS_DATA_DIR
        CleanupManager._remove_directory(target, "embeddings")
    @staticmethod
    def cleanup_vector_store(store_dir: Optional[str] = None) -> None:
        target = store_dir or VECTOR_STORE_DIR
        CleanupManager._remove_directory(target, "vector store")
    @staticmethod
    def cleanup_all() -> None:
        CleanupManager.cleanup_chunks()
        CleanupManager.cleanup_embeddings()
        CleanupManager.cleanup_vector_store()
    @staticmethod
    def _remove_directory(path: str, label: str) -> None:
        if os.path.exists(path):
            shutil.rmtree(path)
            logger.info(f"Cleaned up {label}: {path}")
        else:
            logger.info(f"Nothing to clean ({label}): {path}")