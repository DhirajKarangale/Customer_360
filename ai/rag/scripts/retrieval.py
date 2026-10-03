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

    def retrieve_context(self, user_input: str) -> tuple[str, int]:
        """
        Retrieves relevant context for a given user input.
        Returns a tuple of (compressed_context_string, count_of_retrieved_chunks).
        """

        query_embedding = self._embedder.embed_text(user_input)

        results = self._vector_store.similarity_search(
            query_embedding, top_k=TOP_K, score_threshold=SIMILARITY_SCORE_THRESHOLD
        )
        count = len(results) if results else 0
        if not results:
            return get_message("no_context_found", "No relevant context found."), count

        formatted_context = []
        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            participants = metadata.get("participants", {})
            customer_name = participants.get("customer", {}).get("name", "Unknown")
            mood = metadata.get("user_mood", "neutral")
            doc_type = metadata.get("type", "unknown")
            timestamp = metadata.get("timestamp", "unknown")
            topics = metadata.get("topics", [])
            action_items = metadata.get("action_items", [])

            source_doc = result.get("source_document", "")
            if not source_doc:
                source_doc = metadata.get("source_document", "")
            policy_match = re.search(r"POL-\d+-\d+", source_doc)
            policy_number = policy_match.group(0) if policy_match else "Unknown"

            doc_str = (
                f"### [Document {i}]\n"
                f"**Policy Number:** {policy_number}\n"
                f"**Type:** {doc_type}\n"
                f"**Date:** {timestamp}\n"
                f"**Customer:** {customer_name} (Mood: {mood})\n"
            )
            if topics:
                doc_str += f"**Topics:** {', '.join(topics)}\n"
            if action_items:
                doc_str += f"**Action Items:** {', '.join(action_items)}\n"
            doc_str += f"**Summary:** {result.get('chunk_text', '')}\n"
            formatted_context.append(doc_str)
        return "\n".join(formatted_context), count

    def close(self):
        self._embedder.close()
