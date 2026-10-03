import psycopg2
import psycopg2.extras
from typing import Optional, Dict, Any
class AgentRepository:
    def __init__(self, conn):
        self.conn = conn
    def get_agent_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(
                "SELECT id, name, email, password, phone_number, agency_name, license_number, profile_image_url FROM insurance_agents WHERE email = %s",
                (email,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
    def get_agent_by_id(self, agent_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(
                "SELECT id, name, email, phone_number, agency_name, license_number, profile_image_url, suggestions, suggestions_updated_at FROM insurance_agents WHERE id = %s",
                (agent_id,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
    def update_suggestions(self, agent_id: str, action_text: str):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE insurance_agents 
                SET suggestions = %s, suggestions_updated_at = CURRENT_TIMESTAMP 
                WHERE id = %s
            """,
                (action_text, agent_id),
            )
            self.conn.commit()
        finally:
            cursor.close()