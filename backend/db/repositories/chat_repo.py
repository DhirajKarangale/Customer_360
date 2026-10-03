import psycopg2.extensions
from backend.utils.logger import get_logger
logger = get_logger(__name__)
class ChatRepository:
    def __init__(self, db: psycopg2.extensions.connection):
        self.db = db
    def add_chat(
        self,
        job_id,
        agent_id,
        customer_id,
        policy_id,
        query,
        send_time,
        status="processing",
    ):
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO agent_chats (job_id, agent_id, customer_id, policy_id, query, send_time, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        job_id,
                        agent_id,
                        customer_id,
                        policy_id,
                        query,
                        send_time,
                        status,
                    ),
                )
                self.db.commit()
        except Exception as e:
            logger.error(f"Error adding chat: {e}")
            self.db.rollback()
    def update_chat_message(self, job_id, message, status="completed"):
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE agent_chats 
                    SET message = %s, status = %s
                    WHERE job_id = %s
                """,
                    (message, status, job_id),
                )
                self.db.commit()
        except Exception as e:
            logger.error(f"Error updating chat: {e}")
            self.db.rollback()
    def get_all_chats(self, agent_id):
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT job_id, agent_id, customer_id, policy_id, query, message, status, send_time 
                    FROM agent_chats 
                    WHERE agent_id = %s
                    ORDER BY send_time ASC
                """,
                    (agent_id,),
                )
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching all chats: {e}")
            return []
    def delete_chats_for_agent(self, agent_id):
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """
                    DELETE FROM agent_chats 
                    WHERE agent_id = %s
                """,
                    (agent_id,),
                )
                self.db.commit()
        except Exception as e:
            logger.error(f"Error deleting chats: {e}")
            self.db.rollback()