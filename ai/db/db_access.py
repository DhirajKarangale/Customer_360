import os
import psycopg2
import psycopg2.extras
from ai.utils.common import is_valid_uuid
class AIDatabaseAccess:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )
    def get_agent_context(self, agent_identifier: str) -> str:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            is_uuid = is_valid_uuid(agent_identifier)
            if is_uuid:
                cursor.execute(
                    "SELECT * FROM insurance_agents WHERE id = %s", (agent_identifier,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM insurance_agents WHERE name ILIKE %s LIMIT 1",
                    (f"%{agent_identifier}%",),
                )
            agent = cursor.fetchone()
            if not agent:
                return f"Agent context not found for {agent_identifier}."
            agent_id = agent["id"]
            cursor.execute(
                """
                SELECT status, count(*) as count 
                FROM policies 
                WHERE agent_id = %s 
                GROUP BY status
            """,
                (agent_id,),
            )
            stats = cursor.fetchall()
            res = (
                f"Agent Name: {agent.get('name')}, Agency: {agent.get('agency_name')}\n"
            )
            res += f"- Agent ID: {agent.get('id')}\n"
            res += f"- Email: {agent.get('email')}\n"
            res += f"- Phone: {agent.get('phone_number')}\n"
            res += f"- License Number: {agent.get('license_number')}\n"
            res += f"- Profile Image: {agent.get('profile_image_url')}\n"
            res += f"- Member Since: {agent.get('created_at')}\n"
            res += "Policy Statistics for Agent:\n"
            for stat in stats:
                res += f"- {stat['status']} Policies: {stat['count']}\n"
            return res
        except Exception as e:
            return f"Error fetching agent: {str(e)}"
        finally:
            cursor.close()
    def get_customers_for_agent(self, agent_identifier: str) -> str:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            is_uuid = is_valid_uuid(agent_identifier)
            if is_uuid:
                agent_id = agent_identifier
            else:
                cursor.execute(
                    "SELECT id FROM insurance_agents WHERE name ILIKE %s LIMIT 1",
                    (f"%{agent_identifier}%",),
                )
                agent = cursor.fetchone()
                if not agent:
                    return ""
                agent_id = agent["id"]
            cursor.execute(
                """
                SELECT c.name, c.email, p.status 
                FROM customers c
                JOIN policies p ON c.id = p.customer_id
                WHERE p.agent_id = %s LIMIT 5
            """,
                (agent_id,),
            )
            customers = cursor.fetchall()
            if not customers:
                return "No structured customer data found."
            res = "Structured Customers:\n"
            for c in customers:
                res += f"- Name: {c['name']}, Email: {c['email']}, Policy Status: {c['status']}\n"
            return res
        except Exception as e:
            return f"Error fetching customers: {str(e)}"
        finally:
            cursor.close()
    def close(self):
        if self.conn:
            self.conn.close()
    def get_policy_details(self, policy_id: str) -> str:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            is_uuid = is_valid_uuid(policy_id)
            if is_uuid:
                cursor.execute(
                    """
                    SELECT p.id, p.policy_number, p.policy_type, p.status, p.start_date, p.end_date,
                           p.premium_amount, p.coverage_amount, c.name as customer_name, a.name as agent_name
                    FROM policies p
                    LEFT JOIN customers c ON p.customer_id = c.id
                    LEFT JOIN insurance_agents a ON p.agent_id = a.id
                    WHERE p.id = %s
                """,
                    (policy_id,),
                )
            else:
                cursor.execute(
                    """
                    SELECT p.id, p.policy_number, p.policy_type, p.status, p.start_date, p.end_date,
                           p.premium_amount, p.coverage_amount, c.name as customer_name, a.name as agent_name
                    FROM policies p
                    LEFT JOIN customers c ON p.customer_id = c.id
                    LEFT JOIN insurance_agents a ON p.agent_id = a.id
                    WHERE p.policy_number = %s
                """,
                    (policy_id,),
                )
            policy = cursor.fetchone()
            if not policy:
                return f"No structured database records found for policy {policy_id}."
            res = f"Structured Policy Details for {policy['policy_number']}:\n"
            res += f"- Policy UUID: {policy['id']}\n"
            res += f"- Policy Number: {policy['policy_number']}\n"
            res += f"- Type: {policy['policy_type']}\n"
            res += f"- Status: {policy['status']}\n"
            res += f"- Customer: {policy['customer_name']}\n"
            res += f"- Agent: {policy['agent_name']}\n"
            res += f"- Premium Amount: ${policy['premium_amount']}\n"
            res += f"- Coverage Amount: ${policy['coverage_amount']}\n"
            res += f"- Start Date: {policy['start_date']}\n"
            res += f"- End Date: {policy['end_date']}\n"
            return res
        except Exception as e:
            return f"Error fetching policy details: {str(e)}"
        finally:
            cursor.close()
    def get_customer_details(self, customer_identifier: str) -> str:
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            is_uuid = is_valid_uuid(customer_identifier)
            if is_uuid:
                cursor.execute(
                    "SELECT * FROM customers WHERE id = %s", (customer_identifier,)
                )
            else:
                cursor.execute(
                    "SELECT * FROM customers WHERE name ILIKE %s LIMIT 1",
                    (f"%{customer_identifier}%",),
                )
            customer = cursor.fetchone()
            if not customer:
                return f"No structured database records found for customer {customer_identifier}."
            res = f"Structured Customer Details for {customer['name']}:\n"
            res += f"- Customer ID: {customer['id']}\n"
            res += f"- Email: {customer['email']}\n"
            res += f"- Phone Number: {customer['phone_number']}\n"
            res += f"- Date of Birth: {customer['date_of_birth']}\n"
            res += f"- Address: {customer['address']}\n"
            res += f"- Member Since: {customer['created_at']}\n"
            cursor.execute(
                "SELECT policy_number, status, policy_type FROM policies WHERE customer_id = %s",
                (customer["id"],),
            )
            policies = cursor.fetchall()
            if policies:
                res += "Active/Known Policies:\n"
                for p in policies:
                    res += f"  * {p['policy_number']} ({p['policy_type']} - {p['status']})\n"
            return res
        except Exception as e:
            return f"Error fetching customer details: {str(e)}"
        finally:
            cursor.close()
    def execute_query(self, query: str) -> str:
        """Executes a read-only SQL query and returns the results."""
        if any(
            keyword in query.upper()
            for keyword in [
                "INSERT",
                "UPDATE",
                "DELETE",
                "DROP",
                "ALTER",
                "CREATE",
                "TRUNCATE",
                "GRANT",
                "REVOKE",
                "COMMIT",
            ]
        ):
            return "Error: Only read-only SELECT queries are allowed."
        cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            if not results:
                return "Query returned no results."
            import json
            def default_serializer(obj):
                import datetime
                import uuid
                if isinstance(obj, (datetime.date, datetime.datetime)):
                    return obj.isoformat()
                if isinstance(obj, uuid.UUID):
                    return str(obj)
                from decimal import Decimal
                if isinstance(obj, Decimal):
                    return float(obj)
                return str(obj)
            return json.dumps(results[:100], default=default_serializer, indent=2)
        except Exception as e:
            return f"SQL Error: {str(e)}"
        finally:
            cursor.close()