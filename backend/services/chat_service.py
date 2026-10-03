import os
import redis
from backend.db.repositories.chat_repo import ChatRepository


class ChatService:
    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo

    def add_chat(self, job_id, agent_id, customer_id, policy_id, query, send_time):
        self.chat_repo.add_chat(
            job_id, agent_id, customer_id, policy_id, query, send_time
        )

    def update_chat(self, job_id, message, status="completed"):
        self.chat_repo.update_chat_message(job_id, message, status)

    def get_all_chats(self, agent_id):
        return self.chat_repo.get_all_chats(agent_id)

    def clear_chats(self, agent_id):
        self.chat_repo.delete_chats_for_agent(agent_id)

        try:
            REDIS_URL = os.getenv("REDIS_URL")
            r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

            r.delete(f"agent_memory:{agent_id}")
        except Exception as e:
            import logging

            logging.error(f"Failed to clear redis memory: {e}")
