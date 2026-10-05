import json
import os
import sys
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)
import psycopg2
from dotenv import load_dotenv
env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
)
if not os.path.exists(env_path):
    raise FileNotFoundError(f"Environment file not found at {env_path}")
load_dotenv(env_path)
def get_postgres_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
def main():
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db_backup")
    schema_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "sql", "schema.sql"
    )
    if not os.path.exists(backup_dir):
        logger.info(f"Backup directory not found: {backup_dir}")
        return
    logger.info("Connecting to PostgreSQL for Restore...")
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor()
        logger.info("Dropping existing tables to prepare for restore (CASCADE)...")
        cursor.execute(
            "DROP TABLE IF EXISTS agent_chats, customer_interactions, policies, insurance_agents, customers CASCADE"
        )
        logger.info(f"Recreating tables and indexes from {schema_file}...")
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_sql = f.read()
            cursor.execute(schema_sql)
        conn.commit()
        tables_order = [
            "customers",
            "insurance_agents",
            "policies",
            "customer_interactions",
            "agent_chats",
        ]
        for table in tables_order:
            json_file = os.path.join(backup_dir, f"{table}.json")
            if not os.path.exists(json_file):
                logger.info(
                    f"Backup file for {table} not found at {json_file}. Skipping."
                )
                continue
            with open(json_file, "r", encoding="utf-8") as f:
                rows = json.load(f)
            if not rows:
                logger.info(f"No data to insert for {table}.")
                continue
            logger.info(f"Restoring {len(rows)} rows to {table}...")
            columns = rows[0].keys()
            col_names = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            insert_query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
            data_tuples = [tuple(row[col] for col in columns) for row in rows]
            from psycopg2.extras import execute_batch
            execute_batch(cursor, insert_query, data_tuples)
            conn.commit()
        cursor.close()
        conn.close()
        logger.info("Restore completed successfully!")
    except Exception as e:
        logger.info(f"Error during restore: {e}")
if __name__ == "__main__":
    main()