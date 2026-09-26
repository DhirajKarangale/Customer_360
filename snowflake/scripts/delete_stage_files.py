import os
import snowflake.connector
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
if not os.path.exists(env_path):
    raise FileNotFoundError(f"Environment file not found at {env_path}")
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
        cursor.execute(f"USE WAREHOUSE {SF_WAREHOUSE}")
    if SF_DATABASE:
        cursor.execute(f"USE DATABASE {SF_DATABASE}")
    if SF_SCHEMA:
        cursor.execute(f"USE SCHEMA {SF_SCHEMA}")
    cursor.close()
    return conn

def main():
    print("Connecting to Snowflake...")
    try:
        sf_conn = get_snowflake_conn()
    except Exception as e:
        print(f"Could not connect to Snowflake: {e}")
        return

    cursor = sf_conn.cursor()
    stage_name = "INTERACTIONS_STAGE"
    
    print(f"Removing all files from stage @{stage_name}...")
    try:
        cursor.execute(f"REMOVE @{stage_name}")
        results = cursor.fetchall()
        
        if not results:
            print(f"Stage @{stage_name} was already empty.")
        else:
            print(f"Successfully removed {len(results)} file(s).")
            for row in results:
                print(f"  - Deleted: {row[0]}")
                
    except Exception as e:
        print(f"Failed to remove files: {e}")
    finally:
        cursor.close()
        sf_conn.close()

if __name__ == "__main__":
    main()
