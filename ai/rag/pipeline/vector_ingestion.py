from __future__ import annotations
import json
import os
import time
from typing import Any, Optional
from ai.rag.config import EMBEDDING_DIMENSION, EMBEDDINGS_DATA_DIR, VECTOR_STORE_DIR
from ai.rag.pipeline.faiss_store import VectorStoreManager
from ai.rag.pipeline._utils import discover_json_files
from ai.utils.sound_utils import play_sound
import logging

logger = logging.getLogger(__name__)


class VectorIngestionPipeline:

    def __init__(
        self, embeddings_dir: Optional[str] = None, store_dir: Optional[str] = None
    ) -> None:
        self._embeddings_dir = embeddings_dir or EMBEDDINGS_DATA_DIR
        self._vector_store = VectorStoreManager(
            store_dir or VECTOR_STORE_DIR, EMBEDDING_DIMENSION
        )

    def run(self) -> dict[str, Any]:
        logger.info("=" * 60)
        logger.info("Step C: Vector Store Ingestion")
        logger.info(f"  Input: {self._embeddings_dir}")
        logger.info("=" * 60)
        start_time = time.time()
        self._vector_store.initialize()
        existing_count = self._vector_store.get_document_count()
        logger.info(f"Vector store initialized. Existing vectors: {existing_count}")
        embedding_files = discover_json_files(self._embeddings_dir)
        logger.info(f"Discovered {len(embedding_files)} embedding files.")
        ingested_ids = self._vector_store.get_ingested_document_ids()
        new_files = [f for f in embedding_files if f not in ingested_ids]
        skipped = len(embedding_files) - len(new_files)
        if skipped > 0:
            logger.info(f"Skipping {skipped} already-ingested files.")
        if not new_files:
            logger.info("No new files to ingest.")
            return self._build_summary(
                0, 0, 0, existing_count, time.time() - start_time
            )
        logger.info(f"Ingesting {len(new_files)} new files...")
        logger.info("-" * 60)
        success_count = 0
        error_count = 0
        total_vectors = 0
        for i, rel_path in enumerate(new_files):
            try:
                vec_count = self._ingest_file(rel_path)
                if vec_count is not None:
                    success_count += 1
                    total_vectors += vec_count
                    if (i + 1) % 50 == 0 or success_count == 1:
                        logger.info(
                            f"  [{i + 1}/{len(new_files)}] {rel_path} ({vec_count} vector{('s' if vec_count != 1 else '')})"
                        )
                else:
                    error_count += 1
            except Exception as e:
                logger.info(f"  [ERROR] {rel_path}: {e}")
                error_count += 1
        logger.info("-" * 60)
        logger.info("Saving vector store...")
        self._vector_store.save()
        elapsed = time.time() - start_time
        final_count = self._vector_store.get_document_count()
        summary = self._build_summary(
            success_count, error_count, total_vectors, final_count, elapsed
        )
        self._print_summary(summary)
        if error_count > 0:
            play_sound("error")
        else:
            play_sound("success")
        return summary

    def _ingest_file(self, rel_path: str) -> Optional[int]:
        input_path = os.path.join(self._embeddings_dir, rel_path)
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError, OSError) as e:
            logger.info(f"  [WARN] Failed to read {rel_path}: {e}")
            return None
        entries = data.get("entries")
        if not entries or not isinstance(entries, list):
            logger.info(f"  [WARN] No valid entries in {rel_path}")
            return None
        embeddings: list[list[float]] = []
        chunks: list[dict[str, Any]] = []
        for entry in entries:
            embedding = entry.get("embedding")
            if not embedding:
                continue
            chunk = {k: v for k, v in entry.items() if k != "embedding"}
            embeddings.append(embedding)
            chunks.append(chunk)
        if not embeddings:
            return None
        self._vector_store.add_documents(embeddings, chunks, rel_path)
        return len(embeddings)

    @staticmethod
    def _build_summary(
        success: int,
        errors: int,
        vectors_added: int,
        total_vectors: int,
        elapsed: float,
    ) -> dict[str, Any]:
        return {
            "files_ingested": success,
            "files_failed": errors,
            "vectors_added": vectors_added,
            "total_vectors": total_vectors,
            "elapsed_seconds": round(elapsed, 1),
        }

    @staticmethod
    def _print_summary(summary: dict[str, Any]) -> None:
        logger.info("=" * 60)
        logger.info("Vector Ingestion Summary")
        logger.info(f"  Files ingested:  {summary['files_ingested']}")
        logger.info(f"  Files failed:    {summary['files_failed']}")
        logger.info(f"  Vectors added:   {summary['vectors_added']}")
        logger.info(f"  Total vectors:   {summary['total_vectors']}")
        logger.info(f"  Time:            {summary['elapsed_seconds']}s")
        logger.info("=" * 60)
