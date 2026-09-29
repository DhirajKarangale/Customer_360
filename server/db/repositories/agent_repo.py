import psycopg2
import psycopg2.extras
from typing import Optional, Dict, Any

class AgentRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_agent_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT id, name, email, password, phone_number, agency_name, license_number FROM insurance_agents WHERE email = %s", (email,))
            return cursor.fetchone()
        finally:
            cursor.close()

    def get_agent_by_id(self, agent_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT id, name, email, phone_number, agency_name, license_number FROM insurance_agents WHERE id = %s", (agent_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
