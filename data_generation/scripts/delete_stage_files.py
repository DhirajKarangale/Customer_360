import os
import snowflake.connector
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.sf_auth import get_snowflake_conn

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
if not os.path.exists(env_path):
    raise FileNotFoundError(f"Environment file not found at {env_path}")
load_dotenv(env_path)



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
