import os
import snowflake.connector
from dotenv import load_dotenv
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
SF_USER = os.getenv('SNOWFLAKE_USER')
SF_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SF_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SF_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
SF_DATABASE = os.getenv('SNOWFLAKE_DATABASE')
SF_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA')
PRIVATE_KEY_PATH = os.getenv('SNOWFLAKE_PRIVATE_KEY_PATH')
_GLOBAL_SF_CONN = None


def get_snowflake_conn(force_refresh=False):
    global _GLOBAL_SF_CONN
    if not force_refresh and _GLOBAL_SF_CONN is not None:
        try:
            if not _GLOBAL_SF_CONN.is_closed():
                return _GLOBAL_SF_CONN
        except Exception:
            pass
    if _GLOBAL_SF_CONN is not None:
        try:
            _GLOBAL_SF_CONN.close()
        except Exception:
            pass
    import sys
    try:
        # SPCS Native Auth
        spcs_host = os.getenv("SNOWFLAKE_HOST")
        if spcs_host and os.path.exists("/snowflake/session/token"):
            with open("/snowflake/session/token", "r") as f:
                token = f.read().strip()
            
            connect_kwargs = {
                "host": spcs_host,
                "account": SF_ACCOUNT,
                "authenticator": "oauth",
                "token": token,
            }
        else:
            # Local / External Auth
            connect_kwargs = {
                "user": SF_USER,
                "account": SF_ACCOUNT,
            }
            if SF_PASSWORD:
                connect_kwargs["password"] = SF_PASSWORD
            if PRIVATE_KEY_PATH:
                from cryptography.hazmat.primitives import serialization
                from cryptography.hazmat.backends import default_backend
                with open(PRIVATE_KEY_PATH, "rb") as key:
                    p_key = serialization.load_pem_private_key(
                        key.read(),
                        password=None,
                        backend=default_backend()
                    )
                pkb = p_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
                connect_kwargs["private_key"] = pkb

        conn = snowflake.connector.connect(**connect_kwargs)
    except Exception as e:
        error_str = str(e).lower()
        if 'mfa' in error_str or 'auth' in error_str or 'passcode' in error_str or ('incorrect username or password' in error_str) or ('too many failed' in error_str) or ('locked' in error_str) or ('connection is closed' in error_str):
            print(
                f'\n[CRITICAL] Snowflake Auth/MFA Error in get_snowflake_conn: {e}')
            print(
                'Aborting the entire process to prevent lockout. Please update the passcode and rerun.')
            os._exit(1)
        raise
    cursor = conn.cursor()
    if SF_WAREHOUSE:
        try:
            cursor.execute(f'CREATE WAREHOUSE IF NOT EXISTS {SF_WAREHOUSE}')
        except Exception:
            pass
        cursor.execute(f'USE WAREHOUSE {SF_WAREHOUSE}')
    if SF_DATABASE:
        try:
            cursor.execute(f'CREATE DATABASE IF NOT EXISTS {SF_DATABASE}')
        except Exception:
            pass
        cursor.execute(f'USE DATABASE {SF_DATABASE}')
    if SF_SCHEMA:
        try:
            cursor.execute(f'CREATE SCHEMA IF NOT EXISTS {SF_SCHEMA}')
        except Exception:
            pass
        cursor.execute(f'USE SCHEMA {SF_SCHEMA}')
    cursor.close()
    _GLOBAL_SF_CONN = conn
    return conn
