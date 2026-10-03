from __future__ import annotations
import json
import os
import time
import random
from typing import Any, Optional
from ai.rag.config import (
    CHUNKS_DATA_DIR,
    CLEANED_DATA_DIR,
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL,
    EMBEDDINGS_DATA_DIR,
    OVERRIDE_EMBEDDINGS,
    DIRECT_EMBEDDING_NO_CHUNKING,
    EMBEDDING_MIN_DELAY_SECONDS,
    EMBEDDING_MAX_DELAY_SECONDS,
)
from ai.rag.pipeline.snowflake_embedder import EmbeddingManager
from ai.rag.pipeline._utils import atomic_write_json, discover_json_files
from ai.utils.sound_utils import play_sound
import logging
logger = logging.getLogger(__name__)
class EmbeddingGenerationPipeline:
    def __init__(
        self,
        chunks_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
        override: Optional[bool] = None,
    ) -> None:
        if DIRECT_EMBEDDING_NO_CHUNKING:
            self._chunks_dir = chunks_dir or CLEANED_DATA_DIR
        else:
            self._chunks_dir = chunks_dir or CHUNKS_DATA_DIR
        self._output_dir = output_dir or EMBEDDINGS_DATA_DIR
        self._embedder = EmbeddingManager(EMBEDDING_MODEL, EMBEDDING_DIMENSION)
        self._override = override if override is not None else OVERRIDE_EMBEDDINGS
    def run(self) -> dict[str, Any]:
        logger.info("=" * 60)
        logger.info("Step B: Embedding Generation")
        logger.info(f"  Override: {self._override}")
        logger.info(f"  Input:    {self._chunks_dir}")
        logger.info(f"  Output:   {self._output_dir}")
        logger.info("=" * 60)
        start_time = time.time()
        chunk_files = discover_json_files(self._chunks_dir)
        logger.info(f"Discovered {len(chunk_files)} chunk files.")
        success_count = 0
        skip_count = 0
        error_count = 0
        total_embeddings = 0
        for i, rel_path in enumerate(chunk_files):
            output_path = os.path.join(self._output_dir, rel_path)
            if os.path.exists(output_path) and (not self._override):
                skip_count += 1
                continue
            try:
                emb_count = self._process_chunk_file(rel_path, output_path)
                if emb_count is not None:
                    success_count += 1
                    total_embeddings += emb_count
                    if (i + 1) % 25 == 0 or success_count == 1:
                        logger.info(
                            f"  [{i + 1}/{len(chunk_files)}] {rel_path} ({emb_count} embedding{('s' if emb_count != 1 else '')})"
                        )
                else:
                    error_count += 1
            except Exception as e:
                logger.info(f"  [ERROR] {rel_path}: {e}")
                error_count += 1
        self._embedder.close()
        elapsed = time.time() - start_time
        logger.info("=" * 60)
        logger.info("Embedding Generation Summary")
        logger.info(f"  Processed:  {success_count}")
        logger.info(f"  Skipped:    {skip_count}")
        logger.info(f"  Failed:     {error_count}")
        logger.info(f"  Embeddings: {total_embeddings}")
        logger.info(f"  Time:       {elapsed:.1f}s")
        logger.info("=" * 60)
        if error_count > 0:
            play_sound("error")
        else:
            play_sound("success")
        return {
            "processed": success_count,
            "skipped": skip_count,
            "failed": error_count,
            "total_embeddings": total_embeddings,
            "elapsed_seconds": round(elapsed, 1),
        }
    def _process_chunk_file(self, rel_path: str, output_path: str) -> Optional[int]:
        input_path = os.path.join(self._chunks_dir, rel_path)
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                chunk_data = json.load(f)
        except (json.JSONDecodeError, IOError, OSError) as e:
            logger.info(f"  [WARN] Failed to read {rel_path}: {e}")
            return None
        entries: list[dict[str, Any]] = []
        if DIRECT_EMBEDDING_NO_CHUNKING:
            text = chunk_data.get("content", "")
            metadata = chunk_data.get("metadata", {})
            if text:
                text_to_embed = (
                    f"Metadata: {json.dumps(metadata)}\n\nContent: {text}"
                    if metadata
                    else text
                )
                embedding = self._embedder.embed_text(text_to_embed)
                delay = random.uniform(
                    EMBEDDING_MIN_DELAY_SECONDS, EMBEDDING_MAX_DELAY_SECONDS
                )
                logger.info(
                    f"    [Delay] Waiting for {delay:.1f} seconds to respect rate limits..."
                )
                time.sleep(delay)
                entries.append(
                    {
                        "chunk_text": text,
                        "metadata": chunk_data.get("metadata", {}),
                        "embedding": embedding,
                        "chunk_index": 0,
                        "total_chunks": 1,
                    }
                )
            else:
                logger.info(f"  [WARN] No valid content in {rel_path}")
        else:
            chunks = chunk_data.get("chunks")
            if not chunks or not isinstance(chunks, list):
                logger.info(f"  [WARN] No valid chunks in {rel_path}")
                return None
            for chunk in chunks:
                text = chunk.get("chunk_text", "")
                metadata = chunk.get("metadata", chunk_data.get("metadata", {}))
                if not text:
                    continue
                text_to_embed = (
                    f"Metadata: {json.dumps(metadata)}\n\nContent: {text}"
                    if metadata
                    else text
                )
                embedding = self._embedder.embed_text(text_to_embed)
                delay = random.uniform(
                    EMBEDDING_MIN_DELAY_SECONDS, EMBEDDING_MAX_DELAY_SECONDS
                )
                logger.info(
                    f"    [Delay] Waiting for {delay:.1f} seconds to respect rate limits..."
                )
                time.sleep(delay)
                entry = dict(chunk)
                entry["embedding"] = embedding
                entries.append(entry)
        if not entries:
            return None
        data = {
            "source_document": chunk_data.get("source_document", rel_path),
            "entries": entries,
        }
        atomic_write_json(output_path, data)
        return len(entries)