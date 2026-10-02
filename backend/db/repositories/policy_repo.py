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

            if filters.get("customer_id"):
                cond = " AND customer_id = %s"
                count_query += cond
                data_query += cond
                params.append(filters["customer_id"])

            if filters.get("search_term"):
                term = filters["search_term"]
                like_term = f"%{term}%"
                cond = " AND (id::text = %s OR agent_id::text = %s OR customer_id::text = %s OR policy_number ILIKE %s)"
                count_query += cond
                data_query += cond
                params.extend([term, term, term, like_term])

            cursor.execute(count_query, tuple(params))
            total_items = cursor.fetchone()['total']

            if filters.get("search_term"):
                term = filters["search_term"]
                like_term = f"%{term}%"
                data_query += """ ORDER BY 
                    CASE 
                        WHEN id::text = %s THEN 1
                        WHEN agent_id::text = %s THEN 2
                        WHEN customer_id::text = %s THEN 3
                        WHEN policy_number = %s THEN 4
                        WHEN policy_number ILIKE %s THEN 5
                        ELSE 6
                    END, start_date DESC LIMIT %s OFFSET %s"""
                data_params = params + [term, term, term, term, like_term, page_size, (page - 1) * page_size]
            else:
                data_query += " ORDER BY start_date DESC LIMIT %s OFFSET %s"
                data_params = params + [page_size, (page - 1) * page_size]

            cursor.execute(data_query, tuple(data_params))
            items = cursor.fetchall()
            
            return total_items, items
        finally:
            cursor.close()
