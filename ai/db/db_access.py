import os
import psycopg2
import psycopg2.extras


class AIDatabaseAccess:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
        )

    def get_agent_context(self, agent_id: str) -> str:
        cursor = self.conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("SELECT * FROM insurance_agents WHERE id = %s", (agent_id,))
            agent = cursor.fetchone()
            if not agent:
                return "Agent context not found."
            
            # Fetch aggregate policy statistics for this agent
            cursor.execute("""
                SELECT status, count(*) as count 
                FROM policies 
                WHERE agent_id = %s 
                GROUP BY status
            """, (agent_id,))
            stats = cursor.fetchall()
            
            res = f"Agent Name: {agent.get('name')}, Agency: {agent.get('agency_name')}\n"
            res += "Policy Statistics for Agent:\n"
            for stat in stats:
                res += f"- {stat['status']} Policies: {stat['count']}\n"
                
            return res
        except Exception as e:
            return f"Error fetching agent: {str(e)}"
        finally:
            cursor.close()

    def get_customers_for_agent(self, agent_id: str) -> str:
        cursor = self.conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute("""
                SELECT c.name, c.email, p.status 
                FROM customers c
                JOIN policies p ON c.id = p.customer_id
                WHERE p.agent_id = %s LIMIT 5
            """, (agent_id,))
            customers = cursor.fetchall()
            if not customers:
                return "No structured customer data found."

            res = "Structured Customers:\\n"
            for c in customers:
                res += f"- Name: {c['name']}, Email: {c['email']}, Policy Status: {c['status']}\\n"
            return res
        except Exception as e:
            return f"Error fetching customers: {str(e)}"
        finally:
            cursor.close()

    def close(self):
        if self.conn:
            self.conn.close()
