from __future__ import annotations
import os
import time
from typing import Any, Optional
from rag.config import CLEANED_DATA_DIR, CHUNK_OVERLAP, CHUNK_SIZE, CHUNKS_DATA_DIR, OVERRIDE_CHUNKS
from rag.chunk_manager import ChunkManager
from rag.pipeline.document_loader import DocumentLoader
from rag.pipeline._utils import atomic_write_json
from utils.sound_utils import play_sound

class ChunkGenerationPipeline:

    def __init__(self, data_dir: Optional[str]=None, output_dir: Optional[str]=None, override: Optional[bool]=None) -> None:
        self._loader = DocumentLoader(data_dir or CLEANED_DATA_DIR)
        self._chunker = ChunkManager(CHUNK_SIZE, CHUNK_OVERLAP)
        self._output_dir = output_dir or CHUNKS_DATA_DIR
        self._override = override if override is not None else OVERRIDE_CHUNKS

    def run(self) -> dict[str, Any]:
        print('=' * 60)
        print('Step A: Chunk Generation')
        print(f'  Override: {self._override}')
        print(f'  Output:   {self._output_dir}')
        print('=' * 60)
        start_time = time.time()
        documents = self._loader.discover_documents()
        print(f'Discovered {len(documents)} source documents.')
        success_count = 0
        skip_count = 0
        error_count = 0
        total_chunks = 0
        for i, doc_path in enumerate(documents):
            output_path = os.path.join(self._output_dir, doc_path)
            if os.path.exists(output_path) and (not self._override):
                skip_count += 1
                continue
            try:
                chunk_count = self._process_document(doc_path, output_path)
                if chunk_count is not None:
                    success_count += 1
                    total_chunks += chunk_count
                    if (i + 1) % 50 == 0 or success_count == 1:
                        print(f"  [{i + 1}/{len(documents)}] {doc_path} ({chunk_count} chunk{('s' if chunk_count != 1 else '')})")
                else:
                    error_count += 1
            except Exception as e:
                print(f'  [ERROR] {doc_path}: {e}')
                error_count += 1
        elapsed = time.time() - start_time
        print('=' * 60)
        print('Chunk Generation Summary')
        print(f'  Processed: {success_count}')
        print(f'  Skipped:   {skip_count}')
        print(f'  Failed:    {error_count}')
        print(f'  Chunks:    {total_chunks}')
        print(f'  Time:      {elapsed:.1f}s')
        print('=' * 60)
        if error_count > 0:
            play_sound('error')
        else:
            play_sound('success')
        return {'processed': success_count, 'skipped': skip_count, 'failed': error_count, 'total_chunks': total_chunks, 'elapsed_seconds': round(elapsed, 1)}

    def _process_document(self, doc_path: str, output_path: str) -> Optional[int]:
        doc = self._loader.load_document(doc_path)
        if doc is None:
            return None
        chunk_metadata: dict[str, Any] = {'document_path': doc['document_path'], 'policy_number': doc['policy_number']}
        chunk_metadata.update(doc['metadata'])
        chunks = self._chunker.chunk_document(doc['content'], chunk_metadata)
        if not chunks:
            return None
        data = {'source_document': doc_path, 'chunks': chunks}
        atomic_write_json(output_path, data)
        return len(chunks)