import os
import snowflake.connector
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

SF_USER = os.getenv("SNOWFLAKE_USER")
SF_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SF_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SF_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SF_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SF_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

def get_snowflake_conn():
    conn = snowflake.connector.connect(
        user=SF_USER,
        password=SF_PASSWORD,
        account=SF_ACCOUNT
    )

    cursor = conn.cursor()
    if SF_WAREHOUSE:
        try:
            cursor.execute(f"CREATE WAREHOUSE IF NOT EXISTS {SF_WAREHOUSE}")
        except Exception:
            pass
        cursor.execute(f"USE WAREHOUSE {SF_WAREHOUSE}")
    if SF_DATABASE:
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {SF_DATABASE}")
        except Exception:
            pass
        cursor.execute(f"USE DATABASE {SF_DATABASE}")
    if SF_SCHEMA:
        try:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {SF_SCHEMA}")
        except Exception:
            pass
        cursor.execute(f"USE SCHEMA {SF_SCHEMA}")
    cursor.close()
    
    return conn
