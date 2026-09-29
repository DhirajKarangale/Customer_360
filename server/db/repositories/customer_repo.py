import psycopg2
import psycopg2.extras
from typing import List, Dict, Any, Optional

class CustomerRepository:
    def __init__(self, conn):
        self.conn = conn
        
    def get_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT id, name, email, password, phone_number, date_of_birth, address FROM customers WHERE email = %s", (email,))
            return cursor.fetchone()
        finally:
            cursor.close()

    def get_customers_by_agent(self, agent_id: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            query = """
                SELECT DISTINCT c.id, c.name, c.email, c.phone_number, c.date_of_birth, c.address 
                FROM customers c
                JOIN policies p ON c.id = p.customer_id
                WHERE p.agent_id = %s
            """
            params = [agent_id]

            if filters.get("policy_status"):
                query += " AND p.status = %s"
                params.append(filters["policy_status"])

            if filters.get("policy_type"):
                query += " AND p.policy_type = %s"
                params.append(filters["policy_type"])

            if filters.get("customer_name"):
                query += " AND c.name ILIKE %s"
                params.append(f"%{filters['customer_name']}%")

            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        finally:
            cursor.close()
