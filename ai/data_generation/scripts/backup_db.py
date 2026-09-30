from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))), '.env')
if not os.path.exists(env_path):
    raise FileNotFoundError(f'Environment file not found at {env_path}')
load_dotenv(env_path)
class CustomJSONEncoder(json.JSONEncoder):
    """Custom encoder to handle UUID, datetime, date, and Decimal serialization."""
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)
def get_postgres_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )
def main():
    tables = ['customers', 'insurance_agents',
              'policies', 'customer_interactions']
    backup_dir = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'db_backup')
    os.makedirs(backup_dir, exist_ok=True)
    print("Connecting to PostgreSQL for Backup...")
    try:
        conn = get_postgres_conn()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        for table in tables:
            print(f"Exporting table: {table}...")
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            output_file = os.path.join(backup_dir, f"{table}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(rows, f, cls=CustomJSONEncoder, indent=2)
            print(f"Saved {len(rows)} rows to {output_file}")
        cursor.close()
        conn.close()
        print(
            f"Backup completed successfully! Files are saved in: {backup_dir}")
    except Exception as e:
        print(f"Error during backup: {e}")
if __name__ == "__main__":
    main()
