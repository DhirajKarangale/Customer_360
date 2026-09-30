import os
import sys
import json
import psycopg2
from dotenv import load_dotenv

# Setup path to load .env
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
if not os.path.exists(env_path):
    raise FileNotFoundError(f'Environment file not found at {env_path}')
load_dotenv(env_path)

def get_postgres_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD')
    )

def main():
    conn = get_postgres_conn()
    cursor = conn.cursor()
    
    # 1. Fetch valid policies mapping to customers and agents
    print("Fetching policy mappings from DB...")
    cursor.execute("SELECT policy_number, customer_id::text, agent_id::text FROM policies")
    policy_mapping = {row[0]: (row[1], row[2]) for row in cursor.fetchall()}
    
    # 2. Delete all existing interactions
    print("Deleting existing customer_interactions...")
    cursor.execute("DELETE FROM customer_interactions")
    conn.commit()
    print("Deleted.")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cleaned_dir = os.path.join(base_dir, 'interactions_data', 'cleaned')
    raw_dir = os.path.join(base_dir, 'interactions_data', 'raw')
    
    interactions_to_insert = []
    
    print("Scanning JSON files in cleaned directory...")
    for policy_num in os.listdir(cleaned_dir):
        policy_cleaned_dir = os.path.join(cleaned_dir, policy_num)
        policy_raw_dir = os.path.join(raw_dir, policy_num)
        if not os.path.isdir(policy_cleaned_dir):
            continue
            
        raw_files_dict = {}
        if os.path.isdir(policy_raw_dir):
            for rf in os.listdir(policy_raw_dir):
                base_name = os.path.splitext(rf)[0]
                raw_files_dict[base_name] = rf
        
        for filename in os.listdir(policy_cleaned_dir):
            if not filename.endswith('.json'):
                continue
                
            base_name = os.path.splitext(filename)[0]
            filepath = os.path.join(policy_cleaned_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except Exception:
                    continue
            
            metadata = data.get("metadata", {})
            
            # Use the folder name as the policy_number
            policy_number = policy_num
            
            # Lookup true IDs from our database mapping
            if policy_number not in policy_mapping:
                continue
                
            customer_id, agent_id = policy_mapping[policy_number]
                
            interaction_type = metadata.get("type", "UNKNOWN").upper()
            interaction_date = metadata.get("timestamp")
            policy_number = metadata.get("policy_number", policy_num)
            
            cleaned_data_url = f"@INTERACTIONS_STAGE/cleaned/{policy_num}/{filename}"
            
            raw_filename = raw_files_dict.get(base_name)
            if raw_filename:
                raw_data_url = f"@INTERACTIONS_STAGE/raw/{policy_num}/{raw_filename}"
            else:
                raw_data_url = None
                
            interactions_to_insert.append((
                customer_id,
                agent_id,
                policy_number,
                interaction_type,
                interaction_date,
                raw_data_url,
                cleaned_data_url
            ))
            
    print(f"Found {len(interactions_to_insert)} valid interactions to insert.")
    
    # 3. Insert new data
    insert_query = """
        INSERT INTO customer_interactions (
            customer_id, agent_id, policy_number, 
            interaction_type, interaction_date, 
            raw_data_url, cleaned_data_url
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        from psycopg2.extras import execute_batch
        execute_batch(cursor, insert_query, interactions_to_insert)
        conn.commit()
        print("Successfully repopulated customer_interactions.")
    except Exception as e:
        print(f"Error inserting: {e}")
        conn.rollback()
        
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
