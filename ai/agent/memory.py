import os
import json
import time
import numpy as np
import threading
import redis
from ai.rag.pipeline.snowflake_embedder import EmbeddingManager
from ai.rag.config import EMBEDDING_DIMENSION, EMBEDDING_MODEL
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# We use the sync Redis client because our worker is currently sync.
# We will use threading for the fire-and-forget background tasks.
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Lazy initialize
_redis_client = None
_embedder = None

def get_redis_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingManager(EMBEDDING_MODEL, EMBEDDING_DIMENSION)
    return _embedder

def cosine_similarity(a, b):
    # a: vector, b: array of vectors
    dot_product = np.dot(b, a)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b, axis=1)
    return dot_product / (norm_a * norm_b)

def fetch_and_filter_memory(query: str, agent_id: str) -> list:
    """
    Fetches the last 20 chats from Redis, embeds the query, finds top 5 similar,
    and returns them in chronological order.
    """
    if os.getenv("AGENT_MEMORY", "False").lower() != "true":
        return []

    if not agent_id:
        return []

    try:
        redis_client = get_redis_client()
        key = f"agent_memory:{agent_id}"
        
        # Fetch up to last 20 items
        raw_items = redis_client.lrange(key, 0, 19)
        if not raw_items:
            return []

        items = [json.loads(item) for item in raw_items]
        
        # Prepare embeddings for comparison
        history_embeddings = np.array([item["embedding"] for item in items])
        
        # Embed the new query
        embedder = get_embedder()
        query_embedding = np.array(embedder.embed_text(query))
        
        # Calculate similarity
        similarities = cosine_similarity(query_embedding, history_embeddings)
        
        # Get top 5 indices (or fewer if we have < 5 items)
        top_k = min(5, len(items))
        top_indices = np.argsort(similarities)[-top_k:]
        
        # Sort chronologically (lowest timestamp first)
        selected_items = [items[i] for i in top_indices]
        selected_items.sort(key=lambda x: x.get("timestamp", 0))
        
        # Format as LangChain messages
        formatted_messages = []
        for item in selected_items:
            role = item.get("role")
            content = item.get("content")
            if role == "user":
                formatted_messages.append(HumanMessage(content=content))
            elif role == "ai":
                formatted_messages.append(AIMessage(content=content))
                
        return formatted_messages

    except Exception as e:
        import logging
        logging.error(f"Error fetching memory: {e}")
        return []

def _update_memory_task(agent_id: str, query: str, raw_llm_response: str):
    """
    Background worker function to embed the chat and store it in Redis.
    """
    try:
        redis_client = get_redis_client()
        embedder = get_embedder()
        key = f"agent_memory:{agent_id}"
        
        ts = int(time.time() * 1000)
        
        q_emb = embedder.embed_text(query)
        a_emb = embedder.embed_text(raw_llm_response)
        
        q_obj = {
            "role": "user",
            "content": query,
            "embedding": q_emb,
            "timestamp": ts
        }
        
        a_obj = {
            "role": "ai",
            "content": raw_llm_response,
            "embedding": a_emb,
            "timestamp": ts + 1 # offset slightly to maintain order
        }
        
        # Push to the left (index 0 is newest)
        redis_client.lpush(key, json.dumps(a_obj), json.dumps(q_obj))
        
        # Trim to keep only the last 20 messages
        redis_client.ltrim(key, 0, 19)
        
    except Exception as e:
        import logging
        logging.error(f"Error updating memory in background: {e}")


def update_redis_memory_background(agent_id: str, query: str, raw_llm_response: str):
    """
    Spawns a detached background thread to handle embedding and Redis storage.
    """
    if os.getenv("AGENT_MEMORY", "False").lower() != "true":
        return
        
    if not agent_id:
        return

    # True fire-and-forget
    thread = threading.Thread(
        target=_update_memory_task, 
        args=(agent_id, query, raw_llm_response),
        daemon=True
    )
    thread.start()
