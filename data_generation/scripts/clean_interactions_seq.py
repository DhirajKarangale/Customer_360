import sys
import os
import re
import json
import shutil
import time
import random
from dotenv import load_dotenv

import traceback
import snowflake.connector
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils.sf_auth import get_snowflake_conn
from utils.llm_utils import get_llm, call_llm, LLM_PROVIDER
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

TEST_MODE = False
OVERWRITE_EXISTING = False

MIN_DELAY_SECONDS = 1
MAX_DELAY_SECONDS = 3

MODELS = {
    "CLEANING": "llama3.1-70b",
    "STRUCTURING": "llama3.1-70b"
}

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
if not os.path.exists(env_path):
    raise FileNotFoundError(f"Environment file not found at {env_path}")
load_dotenv(env_path)

def clean_text_locally(raw_text):
    """
    Locally cleans the text using Python.
    Removes extra spaces, empty lines, and specific metadata ids.
    """
    lines = raw_text.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.startswith('mail_id:') or line.startswith('chat_id:') or line.startswith('call_id:'):
            continue
            
        line = re.sub(r'\s+', ' ', line).strip()
        
        if line:
            cleaned_lines.append(line)
            
    return '\n'.join(cleaned_lines)

def semantic_clean_with_llm(sf_conn, text):
    """
    Uses LLM to perform Semantic Normalization, Noise Removal, etc.
    """
    prompt = PromptTemplate.from_template("""
    You are an expert data processor. Please clean the following interaction transcript.
    Apply the following cleaning rules STRICTLY without changing the user's core intent, meaning, or emotion:

    1. Text Cleaning: Fix broken lines and inconsistent casing.
    2. Noise Removal: Remove fillers, repetitions, and conversational noise (e.g., "Uh", "yeah"). Keep meaningful statements.
    3. Semantic Normalization: Make text clear, consistent, and unambiguous.
    4. Vocabulary Standardization: Use standard terms consistently.
    5. Requirement Consistency: Avoid contradictory statements.
    6. Ambiguity Reduction: Remove vague statements. Clearly separate knowns from unknowns.
    7. Language Normalization: Convert informal spoken language into professional text. Improve grammar.
    8. Context Preservation: Preserve uncertainty, suggestions, and original intent.
    9. Canonicalization: Convert different representations of the same entity into a single canonical form.
    10. Preserve Metadata: Do NOT remove any timestamps, participant names, headers, or roles. Preserve them exactly.

    Input Transcript:
    ---
    {text}
    ---

    Provide ONLY the cleaned text. Do NOT include markdown formatting blocks or any conversational filler.
    """)
    
    llm = get_llm(MODELS["CLEANING"])
    if not llm:
        return text
        
    chain = prompt | llm | StrOutputParser()
    
    try:
        result = chain.invoke({"text": text})
        if result:
            if "```" in result:
                result = result.split("```")[1]
                if result.startswith("text") or result.startswith("markdown"):
                    result = result.split('\n', 1)[1]
            return result.strip()
    except Exception as e:
        print(f"Error in semantic cleaning chain: {e}")
        
    return text

def structure_with_llm(sf_conn, raw_text, cleaned_text, file_type):
    """
    Uses LLM to structure the cleaned text into a JSON object with content and metadata.
    """
    prompt = PromptTemplate.from_template("""
    You are an expert AI data structurer building data for a Retrieval-Augmented Generation (RAG) system.
    You are given both the ORIGINAL RAW TEXT (which contains metadata like timestamps, participants, IDs) and the CLEANED TEXT (which is semantically normalized).
    
    Structure the data into a JSON object containing "content" and "metadata".
    
    The file type is known to be: {file_type}

    The JSON MUST follow this exact structure:
    {{
      "content": "<A highly summarized version of what was discussed in the interaction. Focus on the main points, questions, and decisions.>",
      "metadata": {{
        "type": "<call, chat, or email>",
        "timestamp": "<extract exact timestamp from ORIGINAL RAW TEXT. If multiple, use the first/start timestamp. Format: YYYY-MM-DDTHH:MM:SS>",
        "participants": {{
          "customer": {{
            "name": "<name of the customer from ORIGINAL RAW TEXT>",
            "id": "<customer ID (UUID) from ORIGINAL RAW TEXT>"
          }},
          "insurance_agents": [
            {{
              "name": "<agent name from ORIGINAL RAW TEXT>",
              "id": "<agent ID (UUID) from ORIGINAL RAW TEXT>"
            }}
          ]
        }},
        "user_mood": "<e.g., happy, interested, bored, frustrated, angry, confused>",
        "topics": ["<key topics discussed>"],
        "action_items": ["<any next steps or action items mentioned>"]
      }}
    }}

    Rules:
    - You MUST accurately extract timestamps, participant names, and IDs from the ORIGINAL RAW TEXT. Do NOT invent them.
    - The 'content' field should be a concise summary of the conversation, NOT the full text.
    - If the user mood is not explicitly clear, infer it based on the context (e.g., neutral).
    - Ensure output is STRICTLY valid JSON and nothing else. No markdown blocks like ```json.
    
    ORIGINAL RAW TEXT:
    ---
    {raw_text}
    ---
    
    CLEANED TEXT:
    ---
    {cleaned_text}
    ---
    """)
    
    llm = get_llm(MODELS["STRUCTURING"])
    if not llm:
        return None
        
    chain = prompt | llm | StrOutputParser()
    
    try:
        result = chain.invoke({
            "file_type": file_type,
            "raw_text": raw_text,
            "cleaned_text": cleaned_text
        })
        
        if result:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
                
            json_obj = json.loads(result.strip())
            return json.dumps(json_obj, indent=2)
    except json.JSONDecodeError:
        print("Warning: LLM did not return valid JSON. Returning raw string.")
        return result.strip() if result else None
    except Exception as e:
        print(f"Error in structuring chain: {e}")
        
    return None

def process_file(sf_conn, raw_filepath, cleaned_filepath, filename):
    print(f"    Processing file: {filename}")
    with open(raw_filepath, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    local_cleaned = clean_text_locally(raw_text)

    semantic_cleaned = semantic_clean_with_llm(sf_conn, local_cleaned)

    file_type = "call" if filename.endswith('.toon') else "chat or email"
    structured_json = structure_with_llm(sf_conn, raw_text, semantic_cleaned, file_type)

    if structured_json:
        return structured_json
    else:
        print(f"    Failed to process {filename}")
        return None

def process_policy_folder(policy_num, raw_policy_dir, cleaned_policy_dir, sf_conn):
    print(f"  Starting cleaning for Policy: {policy_num}")
    
    files = [f for f in os.listdir(raw_policy_dir) if os.path.isfile(os.path.join(raw_policy_dir, f))]
    if TEST_MODE:
        files = files[:2]
        
    results_to_save = []
    
    for file in files:
        raw_filepath = os.path.join(raw_policy_dir, file)
        cleaned_filepath = os.path.join(cleaned_policy_dir, file)
        
        base_name = os.path.splitext(file)[0]
        expected_json_path = os.path.join(cleaned_policy_dir, f"{base_name}.json")
        
        if os.path.exists(expected_json_path):
            if OVERWRITE_EXISTING:
                print(f"    Overwriting existing {file}")
            else:
                print(f"    Skipping {file} (Already processed)")
                continue
            
        success = False
        for attempt in range(3):
            structured_json = process_file(sf_conn, raw_filepath, cleaned_filepath, file)
            if structured_json:
                results_to_save.append((expected_json_path, structured_json))
                success = True
                break
            else:
                if attempt < 2:
                    print(f"    Retrying {file}... (Attempt {attempt + 2}/3)")
                    time.sleep(2)
                    
        if not success:
            print(f"    Failed to process {file} after 3 attempts. Aborting policy {policy_num} to prevent inconsistencies...")
            if os.path.exists(cleaned_policy_dir):
                try:
                    shutil.rmtree(cleaned_policy_dir)
                except Exception as e:
                    print(f"    Could not delete {cleaned_policy_dir}: {e}")
            return
            
    if results_to_save:
        os.makedirs(cleaned_policy_dir, exist_ok=True)
        for expected_json_path, structured_json in results_to_save:
            with open(expected_json_path, 'w', encoding='utf-8') as f:
                f.write(structured_json)
            print(f"    Saved cleaned JSON to {expected_json_path}")
        
    print(f"  Finished cleaning for Policy: {policy_num}")

from utils.sound_utils import play_sound

def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    raw_dir = os.path.join(base_dir, "interactions_data", "raw")
    cleaned_dir = os.path.join(base_dir, "interactions_data", "cleaned")

    if not os.path.exists(raw_dir):
        print(f"Raw directory not found at {raw_dir}")
        play_sound("error")
        return

    sf_conn = None
    if LLM_PROVIDER.lower() == "snowflake":
        print("Connecting to Snowflake...")
        try:
            sf_conn = get_snowflake_conn()
        except Exception as e:
            print(f"Could not connect to Snowflake: {e}")
            play_sound("error")
            return

    print("Scanning raw directory for policy folders...")
    policy_folders = [f for f in os.listdir(raw_dir) if os.path.isdir(os.path.join(raw_dir, f))]
    
    print(f"Found {len(policy_folders)} policy folders to process.")
    
    if TEST_MODE:
        print("TEST_MODE is enabled. Only processing 2 policy folders.")
        policy_folders = policy_folders[:2]
    
    total_to_process = len(policy_folders)
    print(f"Processing {total_to_process} policies SEQUENTIALLY...")
    
    pipeline_successful = True

    for index, policy_num in enumerate(policy_folders):
        try:
            print(f"\nProcessing Policy {index + 1}/{total_to_process}: {policy_num}")
            
            raw_policy_dir = os.path.join(raw_dir, policy_num)
            cleaned_policy_dir = os.path.join(cleaned_dir, policy_num)
            
            if not OVERWRITE_EXISTING and os.path.exists(cleaned_policy_dir):
                raw_files_count = len([f for f in os.listdir(raw_policy_dir) if os.path.isfile(os.path.join(raw_policy_dir, f))])
                cleaned_files_count = len([f for f in os.listdir(cleaned_policy_dir) if f.endswith('.json')])
                
                if cleaned_files_count >= raw_files_count and raw_files_count > 0:
                    print(f"Skipping Policy {policy_num} (Already completely processed in cleaned folder)")
                    continue

            process_policy_folder(policy_num, raw_policy_dir, cleaned_policy_dir, sf_conn)

            # Wait for a random delay between MIN_DELAY_SECONDS and MAX_DELAY_SECONDS if not the last item
            if index < total_to_process - 1:
                delay = random.randint(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
                print(f"  -> Successfully processed. Waiting for {delay} seconds before the next policy...")
                time.sleep(delay)

        except Exception as e:
            print(f"\n[!] ERROR OCCURRED during processing policy '{policy_num}':")
            traceback.print_exc()
            print("Stopping the pipeline and sounding alarm...")
            pipeline_successful = False
            play_sound("error")
            break

    if sf_conn:
        sf_conn.close()
    print("\nCleaning pipeline finished!")
    
    if pipeline_successful and total_to_process > 0:
        print("  -> All policies processed! Playing success chime...")
        play_sound("success")

if __name__ == "__main__":
    main()
