import os
import random
import json
import psycopg2
import snowflake.connector
from dotenv import load_dotenv
from sf_auth import get_snowflake_conn
import concurrent.futures

START_POLICY = 121
END_POLICY = 125

MAX_WORKERS = 5

MIN_INTERACTIONS = 4
MAX_INTERACTIONS = 8

MODELS = {
    "SEQUENCE": "llama3.1-8b",
    "TRANSCRIPT": "llama3.1-70b",
    "SUMMARY": "llama3.1-8b"
}

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
if not os.path.exists(env_path):
    raise FileNotFoundError(f"Environment file not found at {env_path}")
load_dotenv(env_path)

SCHEMA_PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts', 'llm_schema_prompt.md')
SCHEMA_PROMPT = ""
if os.path.exists(SCHEMA_PROMPT_PATH):
    with open(SCHEMA_PROMPT_PATH, "r", encoding="utf-8") as f:
        SCHEMA_PROMPT = f.read()

PG_HOST = os.getenv("POSTGRES_HOST")
PG_PORT = os.getenv("POSTGRES_PORT")
PG_NAME = os.getenv("POSTGRES_DB")
PG_USER = os.getenv("POSTGRES_USER")
PG_PASS = os.getenv("POSTGRES_PASSWORD")



def get_postgres_conn():
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_NAME,
        user=PG_USER,
        password=PG_PASS
    )

def fetch_all_policy_data():
    conn = get_postgres_conn()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        p.policy_number, p.policy_type, p.status, p.start_date, p.end_date, p.premium_amount, p.coverage_amount,
        c.name AS customer_name, c.email AS customer_email, c.phone_number AS customer_phone,
        a.name AS agent_name, a.agency_name
    FROM policies p
    JOIN customers c ON p.customer_id = c.id
    JOIN insurance_agents a ON p.agent_id = a.id
    """
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    return data

def call_cortex_llm(sf_conn, prompt, model_name):
    cursor = sf_conn.cursor()
    
    query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model_name}', %s)"
    try:
        cursor.execute(query, (prompt,))
        result = cursor.fetchone()[0]
        return result
    except Exception as e:
        print(f"Error calling Cortex: {e}")
        return None
    finally:
        cursor.close()

def generate_interaction_sequence(sf_conn, policy):
    num_interactions = random.randint(MIN_INTERACTIONS, MAX_INTERACTIONS)
    prompt = f"""
    You are an AI planning interactions. 
    Customer '{policy['customer_name']}' is interacting with Insurance Agent '{policy['agent_name']}' 
    regarding a {policy['policy_type']} policy (Status: {policy['status']}).
    Generate a logical sequence of exactly {num_interactions} interactions using channels (Call, Email, or Chat).
    OUTPUT STRICTLY A VALID JSON LIST OF STRINGS AND NOTHING ELSE. Do NOT include markdown blocks, numbers, or conversational text.
    Correct format example: ["Call", "Email", "Chat", "Call", "Email"]
    """
    
    result = call_cortex_llm(sf_conn, prompt, MODELS["SEQUENCE"])
    try:
        if result:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
                
            start_idx = result.find('[')
            end_idx = result.rfind(']')
            if start_idx != -1 and end_idx != -1:
                result = result[start_idx:end_idx+1]
                
            sequence = json.loads(result.strip())
            if isinstance(sequence, list) and len(sequence) > 0:
                while len(sequence) < num_interactions:
                    sequence.append(random.choice(["Call", "Email", "Chat"]))
                return sequence[:num_interactions]
    except Exception as e:
        pass
    
    fallback = ["Email", "Call", "Chat", "Call", "Email", "Chat", "Call", "Email", "Call", "Chat"]
    return fallback[:num_interactions]

def generate_interaction_content(sf_conn, policy, sequence, policy_dir):
    context = ""
    
    for i, channel in enumerate(sequence):
        step_num = i + 1
        
        is_long_call = (channel == "Call" and random.random() < 0.15)
        if is_long_call:
            length_desc = "This is a VERY LONG call (10-20 minutes). Include timestamps jumping by minutes, hold music breaks, background noise (e.g., [typing], [dog barks]), extensive troubleshooting, and small talk."
        elif channel == "Call":
            length_desc = "This is a normal length call (2-5 minutes). Include some timestamps (e.g., [00:00])."
        elif channel == "Chat":
            length_desc = "This is a live chat. Include timestamps, typos, corrections (*word), and slight delays."
        else:
            length_desc = "This is an email thread. Include realistic email headers, dates, and sign-offs."

        if channel == "Call":
            human_instructions = "- Do not use perfect grammar. Humans hesitate (Umm, ah). Humans interrupt each other (--). Add annotations like [sighs], [typing]. Add emotion if policy is Cancelled/Expired."
        elif channel == "Chat":
            human_instructions = "- Use a slightly informal tone. Customers might use lower case, abbreviations, or have typos. Include corrections (*word). Add emotion if policy is Cancelled/Expired."
        else:
            human_instructions = "- Write in a natural business tone, not a robotic template. The customer can be direct or frustrated if policy is Cancelled/Expired. The agent is professional but empathetic."

        prompt = f"""
        You are an expert transcript/data generator. Write interaction #{step_num} of {len(sequence)} ({channel}).
        Company Name: DCoders
        Customer: {policy['customer_name']}
        Agent: {policy['agent_name']} (Agency: {policy['agency_name']})
        Policy Details: {policy['policy_type']} policy. Target end status of this policy in the system is '{policy['status']}'.
        
        Previous context (if any): {context if context else 'This is the first interaction.'}
        
        {length_desc}
        
        CRITICAL INSTRUCTIONS TO AVOID SOUNDING LIKE A ROBOT:
        {human_instructions}
        - Ensure the interaction data is highly detailed, rich in context, and comprehensive.
        
        You MUST follow the schema definitions below for your output.
        Only output the raw textual data matching the {channel} schema, no extra meta commentary.
        
        --- SCHEMA DEFINITIONS ---
        {SCHEMA_PROMPT}
        """
        
        content = call_cortex_llm(sf_conn, prompt, MODELS["TRANSCRIPT"])
        
        if content:
            if "```text" in content:
                content = content.split("```text")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            ext = ".toon" if channel == "Call" else ".txt"
            file_path = os.path.join(policy_dir, f"{step_num}_{channel}{ext}")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content.strip())
            
            summary_prompt = f"Summarize this interaction in 1 or 2 short sentences:\n\n{content.strip()}"
            summary = call_cortex_llm(sf_conn, summary_prompt, MODELS["SUMMARY"])
            if summary:
                context += f"Step {step_num} ({channel}): {summary.strip()}\n"
            else:
                context += f"Step {step_num} ({channel}) occurred.\n"
        else:
            print(f"    [Content Generation Failed for step {step_num}]")

def process_policy(index, policy, total_in_batch, output_dir, sf_conn):
    p_num = policy['policy_number']
    print(f"\nProcessing Policy {index + 1}/{total_in_batch}: {p_num}")
    
    policy_dir = os.path.join(output_dir, p_num)
    os.makedirs(policy_dir, exist_ok=True)
    
    sequence = generate_interaction_sequence(sf_conn, policy)
    print(f"  [{p_num}] Sequence planned: {sequence}")
    
    generate_interaction_content(sf_conn, policy, sequence, policy_dir)
    
    print(f"  [{p_num}] Saved files to {policy_dir}")


def main():
    print("Fetching policy data from PostgreSQL...")
    policies = fetch_all_policy_data()
    print(f"Found {len(policies)} policies.")
    
    print("Connecting to Snowflake...")
    try:
        sf_conn = get_snowflake_conn()
    except Exception as e:
        print(f"Could not connect to Snowflake: {e}")
        return

    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "interactions_data", "raw")
    os.makedirs(output_dir, exist_ok=True)
    
    start_index = START_POLICY - 1
    end_index = END_POLICY
    policies_to_process = policies[start_index:end_index]
    
    print(f"Processing {len(policies_to_process)} policy using {MAX_WORKERS} workers...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for index, policy in enumerate(policies_to_process):
            futures.append(executor.submit(process_policy, index, policy, len(policies_to_process), output_dir, sf_conn))
            
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing policy: {e}")

    sf_conn.close()
    print("\nData generation complete!")

if __name__ == "__main__":
    main()
