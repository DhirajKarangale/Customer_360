import os
import sys
import psycopg2
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
if not os.path.exists(env_path):
    raise FileNotFoundError(f'Environment file not found at {env_path}')
load_dotenv(env_path)

PG_HOST = os.getenv('POSTGRES_HOST')
PG_PORT = os.getenv('POSTGRES_PORT')
PG_NAME = os.getenv('POSTGRES_DB')
PG_USER = os.getenv('POSTGRES_USER')
PG_PASS = os.getenv('POSTGRES_PASSWORD')

def get_postgres_conn():
    return psycopg2.connect(host=PG_HOST, port=PG_PORT, dbname=PG_NAME, user=PG_USER, password=PG_PASS)

def main():
    print("Connecting to PostgreSQL...")
    conn = get_postgres_conn()
    cursor = conn.cursor()

    # Fetch policies to map policy_number to customer_id and agent_id
    print("Fetching policies...")
    cursor.execute("SELECT policy_number, customer_id, agent_id FROM policies")
    policies = {row[0]: {'customer_id': row[1], 'agent_id': row[2]} for row in cursor.fetchall()}
    print(f"Found {len(policies)} policies in DB.")

    base_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'interactions_data')
    raw_dir = os.path.join(base_data_dir, 'raw')
    
    if not os.path.exists(raw_dir):
        print(f"Raw data directory not found: {raw_dir}")
        return

    interactions_to_insert = []
    
    print("Scanning local raw files...")
    for policy_num in os.listdir(raw_dir):
        policy_path = os.path.join(raw_dir, policy_num)
        if not os.path.isdir(policy_path):
            continue
            
        if policy_num not in policies:
            print(f"Warning: Policy {policy_num} found in files but not in DB.")
            continue
            
        customer_id = policies[policy_num]['customer_id']
        agent_id = policies[policy_num]['agent_id']
        
        for file in os.listdir(policy_path):
            # Parse filename e.g. 1_Call.toon
            name_parts = file.split('_')
            if len(name_parts) < 2:
                continue
                
            type_part = name_parts[1].split('.')[0].upper()
            if type_part not in ['CALL', 'EMAIL', 'CHAT']:
                interaction_type = 'OTHER'
            else:
                interaction_type = type_part
                
            raw_url = f"@INTERACTIONS_STAGE/raw/{policy_num}/{file}"
            
            # Cleaned data filename has .json extension
            clean_file = file.rsplit('.', 1)[0] + '.json'
            clean_url = f"@INTERACTIONS_STAGE/cleaned/{policy_num}/{clean_file}"
            
            interactions_to_insert.append((
                customer_id,
                agent_id,
                interaction_type,
                raw_url,
                clean_url
            ))

    print(f"Prepared {len(interactions_to_insert)} interactions for insertion.")
    
    if interactions_to_insert:
        # Clear existing interactions to prevent duplicates on multiple runs
        print("Clearing existing interactions...")
        cursor.execute("TRUNCATE TABLE customer_interactions RESTART IDENTITY CASCADE")
        
        print("Inserting into customer_interactions...")
        insert_query = """
            INSERT INTO customer_interactions (customer_id, agent_id, interaction_type, raw_data_url, cleaned_data_url)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        # Batch insert
        from psycopg2.extras import execute_batch
        execute_batch(cursor, insert_query, interactions_to_insert)
        
        conn.commit()
        print("Successfully updated customer_interactions table.")
    else:
        print("No interactions found to insert.")
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
