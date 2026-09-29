import psycopg2
import psycopg2.extras
from typing import List, Dict, Any, Optional, Tuple

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

    def get_customers_by_agent(self, agent_id: str, filters: Dict[str, Any], page: int, page_size: int) -> Tuple[int, List[Dict[str, Any]]]:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            count_query = """
                SELECT COUNT(DISTINCT c.id) as total
                FROM customers c
                JOIN policies p ON c.id = p.customer_id
                WHERE p.agent_id = %s
            """
            
            data_query = """
                SELECT DISTINCT c.id, c.name, c.email, c.phone_number, c.date_of_birth, c.address 
                FROM customers c
                JOIN policies p ON c.id = p.customer_id
                WHERE p.agent_id = %s
            """
            params = [agent_id]

            if filters.get("policy_status"):
                cond = " AND p.status = %s"
                count_query += cond
                data_query += cond
                params.append(filters["policy_status"])

            if filters.get("policy_type"):
                cond = " AND p.policy_type = %s"
                count_query += cond
                data_query += cond
                params.append(filters["policy_type"])

            if filters.get("customer_name"):
                cond = " AND c.name ILIKE %s"
                count_query += cond
                data_query += cond
                params.append(f"%{filters['customer_name']}%")

            cursor.execute(count_query, tuple(params))
            total_items = cursor.fetchone()['total']

            data_query += " ORDER BY c.name LIMIT %s OFFSET %s"
            data_params = params + [page_size, (page - 1) * page_size]

            cursor.execute(data_query, tuple(data_params))
            items = cursor.fetchall()
            
            return total_items, items
        finally:
            cursor.close()
