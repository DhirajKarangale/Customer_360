import psycopg2
import psycopg2.extras
from typing import List, Dict, Any, Tuple

class PolicyRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_policies_by_agent(self, agent_id: str, filters: Dict[str, Any], page: int, page_size: int) -> Tuple[int, List[Dict[str, Any]]]:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            count_query = "SELECT COUNT(*) as total FROM policies WHERE agent_id = %s"
            data_query = "SELECT id, policy_number, customer_id, agent_id, policy_type, status, start_date, end_date, premium_amount, coverage_amount FROM policies WHERE agent_id = %s"
            params = [agent_id]

            if filters.get("status"):
                cond = " AND status = %s"
                count_query += cond
                data_query += cond
                params.append(filters["status"])
            
            if filters.get("policy_type"):
                cond = " AND policy_type = %s"
                count_query += cond
                data_query += cond
                params.append(filters["policy_type"])

            cursor.execute(count_query, tuple(params))
            total_items = cursor.fetchone()['total']

            data_query += " ORDER BY start_date DESC LIMIT %s OFFSET %s"
            data_params = params + [page_size, (page - 1) * page_size]

            cursor.execute(data_query, tuple(data_params))
            items = cursor.fetchall()
            
            return total_items, items
        finally:
            cursor.close()
