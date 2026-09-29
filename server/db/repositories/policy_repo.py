import psycopg2
import psycopg2.extras
from typing import List, Dict, Any

class PolicyRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_policies_by_agent(self, agent_id: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            query = "SELECT id, policy_number, customer_id, agent_id, policy_type, status, start_date, end_date, premium_amount, coverage_amount FROM policies WHERE agent_id = %s"
            params = [agent_id]

            if filters.get("status"):
                query += " AND status = %s"
                params.append(filters["status"])
            
            if filters.get("policy_type"):
                query += " AND policy_type = %s"
                params.append(filters["policy_type"])

            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        finally:
            cursor.close()
