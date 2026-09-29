import json
from rag.config import EMBEDDING_DIMENSION, EMBEDDING_MODEL, SIMILARITY_SCORE_THRESHOLD, TOP_K, VECTOR_STORE_DIR
from rag.embedding_manager import EmbeddingManager
from rag.vector_manager import VectorStoreManager

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
        # Generate the query embedding
        query_embedding = self._embedder.embed_text(user_input)
        
        # Perform vector similarity search and filter using threshold and top_k
        results = self._vector_store.similarity_search(
            query_embedding,
            top_k=TOP_K,
            score_threshold=SIMILARITY_SCORE_THRESHOLD
        )
        
        count = len(results) if results else 0
        if not results:
            return "No relevant context found.", count
            
        # Retrieve matching chunks and their complete metadata/context
        formatted_context = []
        for result in results:
            # Compress JSON by omitting spaces to lower token count
            formatted_context.append(json.dumps(result, separators=(',', ':')))
            
        # Return only the final relevant context and count
        return "\n".join(formatted_context), count

    def close(self):
        self._embedder.close()
