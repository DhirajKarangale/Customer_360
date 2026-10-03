import json
import os
import random
import shutil
import sys
import time
import logging

logger = logging.getLogger(__name__)

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)

import concurrent.futures
from ai.utils.sound_utils import play_sound
from langchain_core.output_parsers import StrOutputParser
from ai.utils.prompts import (
    SEQUENCE_GENERATION_PROMPT,
    TRANSCRIPT_GENERATION_PROMPT,
    SUMMARY_PROMPT,
)
from ai.utils.llm_utils import get_llm
import psycopg2
from dotenv import load_dotenv

START_POLICY = 121
END_POLICY = 125
MAX_WORKERS = 5
MIN_INTERACTIONS = 4
MAX_INTERACTIONS = 8
env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
)
if not os.path.exists(env_path):
    raise FileNotFoundError(f"Environment file not found at {env_path}")
load_dotenv(env_path)
SCHEMA_PROMPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "prompts", "llm_schema_prompt.md"
)
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
        host=PG_HOST, port=PG_PORT, dbname=PG_NAME, user=PG_USER, password=PG_PASS
    )


def fetch_all_policy_data():
    conn = get_postgres_conn()
    cursor = conn.cursor()
    query = "\n    SELECT \n        p.policy_number, p.policy_type, p.status, p.start_date, p.end_date, p.premium_amount, p.coverage_amount,\n        c.name AS customer_name, c.email AS customer_email, c.phone_number AS customer_phone,\n        a.name AS agent_name, a.agency_name\n    FROM policies p\n    JOIN customers c ON p.customer_id = c.id\n    JOIN insurance_agents a ON p.agent_id = a.id\n    "
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    data = [dict(zip(columns, row)) for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return data


def generate_interaction_sequence(policy):
    num_interactions = random.randint(MIN_INTERACTIONS, MAX_INTERACTIONS)
    prompt = SEQUENCE_GENERATION_PROMPT.format(
        customer_name=policy["customer_name"],
        agent_name=policy["agent_name"],
        policy_type=policy["policy_type"],
        status=policy["status"],
        num_interactions=num_interactions,
    )
    try:
        chain = get_llm("SEQUENCE") | StrOutputParser()
        result = chain.invoke(prompt)
    except Exception as e:
        logger.info(f"Error calling LLM: {e}")
        result = None
    try:
        if result:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            start_idx = result.find("[")
            end_idx = result.rfind("]")
            if start_idx != -1 and end_idx != -1:
                result = result[start_idx : end_idx + 1]
            sequence = json.loads(result.strip())
            if isinstance(sequence, list) and len(sequence) > 0:
                while len(sequence) < num_interactions:
                    sequence.append(random.choice(["Call", "Email", "Chat"]))
                return sequence[:num_interactions]
    except Exception as e:
        pass
    fallback = [
        "Email",
        "Call",
        "Chat",
        "Call",
        "Email",
        "Chat",
        "Call",
        "Email",
        "Call",
        "Chat",
    ]
    return fallback[:num_interactions]


def generate_interaction_content(policy, sequence, policy_dir):
    context = ""
    results_to_save = []
    for i, channel in enumerate(sequence):
        step_num = i + 1
        is_long_call = channel == "Call" and random.random() < 0.15
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
        prompt = TRANSCRIPT_GENERATION_PROMPT.format(
            step_num=step_num,
            total_steps=len(sequence),
            channel=channel,
            customer_name=policy["customer_name"],
            agent_name=policy["agent_name"],
            agency_name=policy["agency_name"],
            policy_type=policy["policy_type"],
            status=policy["status"],
            context=context if context else "This is the first interaction.",
            length_desc=length_desc,
            human_instructions=human_instructions,
            schema_prompt=SCHEMA_PROMPT,
        )
        success = False
        for attempt in range(3):
            try:
                chain = get_llm("TRANSCRIPT") | StrOutputParser()
                content = chain.invoke(prompt)
            except Exception as e:
                logger.info(f"Error calling LLM: {e}")
                content = None
            if content:
                if "```text" in content:
                    content = content.split("```text")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                ext = ".toon" if channel == "Call" else ".txt"
                file_path = os.path.join(policy_dir, f"{step_num}_{channel}{ext}")
                results_to_save.append((file_path, content.strip()))
                summary_prompt = SUMMARY_PROMPT.format(content=content.strip())
                try:
                    chain = get_llm("SUMMARY") | StrOutputParser()
                    summary = chain.invoke(summary_prompt)
                except Exception as e:
                    logger.info(f"Error calling LLM: {e}")
                    summary = None
                if summary:
                    context += f"Step {step_num} ({channel}): {summary.strip()}\n"
                else:
                    context += f"Step {step_num} ({channel}) occurred.\n"
                success = True
                break
            elif attempt < 2:
                logger.info(f"    [Retry {attempt + 2}/3 for step {step_num}]")
                time.sleep(2)
        if not success:
            logger.info(
                f"    [Content Generation Failed for step {step_num} after 3 attempts]"
            )
            return None
    return results_to_save


def process_policy(index, policy, total_in_batch, output_dir):
    p_num = policy["policy_number"]
    logger.info(f"\nProcessing Policy {index + 1}/{total_in_batch}: {p_num}")
    policy_dir = os.path.join(output_dir, p_num)
    sequence = generate_interaction_sequence(policy)
    logger.info(f"  [{p_num}] Sequence planned: {sequence}")
    results = generate_interaction_content(policy, sequence, policy_dir)
    if results:
        os.makedirs(policy_dir, exist_ok=True)
        for file_path, content in results:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        logger.info(f"  [{p_num}] Saved files to {policy_dir}")
    else:
        logger.info(f"  [{p_num}] Aborted to prevent inconsistencies.")
        if os.path.exists(policy_dir):
            try:
                shutil.rmtree(policy_dir)
            except Exception as e:
                pass


def main():
    logger.info("Fetching policy data from PostgreSQL...")
    try:
        policies = fetch_all_policy_data()
    except Exception as e:
        logger.info(f"Failed to fetch policies: {e}")
        play_sound("error")
        return
    logger.info(f"Found {len(policies)} policies.")
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "interactions_data", "raw"
    )
    os.makedirs(output_dir, exist_ok=True)
    start_index = START_POLICY - 1
    end_index = END_POLICY
    policies_to_process = policies[start_index:end_index]
    logger.info(
        f"Processing {len(policies_to_process)} policy using {MAX_WORKERS} workers..."
    )
    pipeline_successful = True
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for index, policy in enumerate(policies_to_process):
            futures.append(
                executor.submit(
                    process_policy, index, policy, len(policies_to_process), output_dir
                )
            )
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.info(f"Error processing policy: {e}")
                pipeline_successful = False
    logger.info("\nData generation complete!")
    if pipeline_successful:
        play_sound("success")
    else:
        play_sound("error")


if __name__ == "__main__":
    main()
