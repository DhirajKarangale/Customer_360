import os
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
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
KEY_REQUIRED = os.getenv("KEY_REQUIRED", "false").lower() == "true"

def get_snowflake_conn():
    if KEY_REQUIRED:
        key_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "rsa_key.p8")
        with open(key_path, "rb") as key_file:
            p_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )

        pkb = p_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        conn = snowflake.connector.connect(
            user=SF_USER,
            account=SF_ACCOUNT,
            private_key=pkb
        )
    else:
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
