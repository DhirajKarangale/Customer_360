import os
import snowflake.connector
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

SF_USER = os.getenv("SNOWFLAKE_USER")
SF_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SF_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SF_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SF_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SF_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

def get_snowflake_conn():
    import sys
    try:
        conn = snowflake.connector.connect(
            user=SF_USER,
            password=SF_PASSWORD,
            account=SF_ACCOUNT
        )
    except Exception as e:
        error_str = str(e).lower()
        if "mfa" in error_str or "auth" in error_str or "passcode" in error_str or "incorrect username or password" in error_str or "too many failed" in error_str or "locked" in error_str or "connection is closed" in error_str:
            print(f"\n[CRITICAL] Snowflake Auth/MFA Error in get_snowflake_conn: {e}")
            print("Aborting the entire process to prevent lockout. Please update the passcode and rerun.")
            os._exit(1)
        raise

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
