import os
import json
import time
import threading
import redis
from langchain_core.messages import HumanMessage, AIMessage
REDIS_URL = os.getenv("REDIS_URL")
MAX_TURNS = 3
_redis_client = None
def _get_redis():
    """Returns a module-level Redis client for the main thread."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client
def _memory_enabled() -> bool:
    return os.getenv("AGENT_MEMORY").lower() == "true"
def _make_key(agent_id: str) -> str:
    return f"agent_memory:{agent_id}"
def fetch_and_filter_memory(query: str, agent_id: str) -> list:
    """
    Returns the last MAX_TURNS conversation turns from Redis as LangChain messages.
    No embeddings, no similarity search — just raw chronological context injected
    into the conversation history. Simple, fast, zero Snowflake calls.
    """
    if not _memory_enabled() or not agent_id:
        return []
    try:
        r = _get_redis()
        key = _make_key(agent_id)
        raw_items = r.lrange(key, 0, MAX_TURNS - 1)
        if not raw_items:
            return []
        turns = [json.loads(item) for item in reversed(raw_items)]
        messages = []
        for turn in turns:
            user_msg = turn.get("user", "")
            ai_msg = turn.get("ai", "")
            if user_msg:
                messages.append(HumanMessage(content=user_msg))
            if ai_msg:
                messages.append(AIMessage(content=ai_msg))
        return messages
    except Exception as e:
        import logging
        logging.warning(f"[Memory] Failed to fetch memory for agent {agent_id}: {e}")
        return []
def _update_memory_task(agent_id: str, query: str, raw_llm_response: str):
    """
    Background thread: stores one conversation turn in Redis.
    Uses its own Redis connection (thread-safe, no shared state).
    No Snowflake calls — no embeddings.
    """
    try:
        r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        key = _make_key(agent_id)
        user_content = query.strip()[:800]
        ai_content = raw_llm_response.strip()[:800]
        turn = {"user": user_content, "ai": ai_content, "ts": int(time.time() * 1000)}
        r.lpush(key, json.dumps(turn))
        r.ltrim(key, 0, MAX_TURNS - 1)
    except Exception as e:
        import logging
        logging.error(
            f"[Memory] Background memory update failed for agent {agent_id}: {e}"
        )
def update_redis_memory_background(agent_id: str, query: str, raw_llm_response: str):
    """
    Fire-and-forget: spawns a daemon thread to persist the conversation turn.
    Does NOT block the response path.
    """
    if not _memory_enabled() or not agent_id:
        return
    if not query or not raw_llm_response:
        return
    thread = threading.Thread(
        target=_update_memory_task,
        args=(agent_id, query, raw_llm_response),
        daemon=True,
    )
    thread.start()