import json
import os
import random
import re
import shutil
import sys
import time
import traceback
import logging

logger = logging.getLogger(__name__)

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ),
)

from ai.utils.sound_utils import play_sound
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from ai.utils.prompts import CLEANING_PROMPT, STRUCTURING_PROMPT
from ai.utils.llm_utils import get_llm
from dotenv import load_dotenv

TEST_MODE = False
OVERWRITE_EXISTING = False
MIN_DELAY_SECONDS = 1
MAX_DELAY_SECONDS = 3
env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
)
if not os.path.exists(env_path):
    raise FileNotFoundError(f"Environment file not found at {env_path}")
load_dotenv(env_path)


def clean_text_locally(raw_text):
    lines = raw_text.split("\n")
    cleaned_lines = []
    for line in lines:
        if (
            line.startswith("mail_id:")
            or line.startswith("chat_id:")
            or line.startswith("call_id:")
        ):
            continue
        line = re.sub("\\s+", " ", line).strip()
        if line:
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def semantic_clean_with_llm(text):
    prompt = PromptTemplate.from_template(CLEANING_PROMPT)
    llm = get_llm("CLEANING")
    if not llm:
        return text
    chain = prompt | llm | StrOutputParser()
    try:
        result = chain.invoke({"text": text})
        if result:
            if "```" in result:
                result = result.split("```")[1]
                if result.startswith("text") or result.startswith("markdown"):
                    result = result.split("\n", 1)[1]
            return result.strip()
    except Exception as e:
        logger.info(f"Error in semantic cleaning chain: {e}")
    return text


def structure_with_llm(raw_text, cleaned_text, file_type, policy_num):
    prompt = PromptTemplate.from_template(STRUCTURING_PROMPT)
    llm = get_llm("STRUCTURING")
    if not llm:
        return None
    chain = prompt | llm | StrOutputParser()
    try:
        result = chain.invoke(
            {"file_type": file_type, "raw_text": raw_text, "cleaned_text": cleaned_text}
        )
        if result:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            json_obj = json.loads(result.strip())
            if "metadata" not in json_obj:
                json_obj["metadata"] = {}
            json_obj["metadata"]["policy_number"] = policy_num
            return json.dumps(json_obj, indent=2)
    except json.JSONDecodeError:
        logger.info("Warning: LLM did not return valid JSON. Returning raw string.")
        return result.strip() if result else None
    except Exception as e:
        logger.info(f"Error in structuring chain: {e}")
    return None


def process_file(raw_filepath, cleaned_filepath, filename, policy_num):
    logger.info(f"    Processing file: {filename}")
    with open(raw_filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()
    local_cleaned = clean_text_locally(raw_text)
    semantic_cleaned = semantic_clean_with_llm(local_cleaned)
    file_type = "call" if filename.endswith(".toon") else "chat or email"
    structured_json = structure_with_llm(
        raw_text, semantic_cleaned, file_type, policy_num
    )
    if structured_json:
        return structured_json
    else:
        logger.info(f"    Failed to process {filename}")
        return None


def process_policy_folder(policy_num, raw_policy_dir, cleaned_policy_dir):
    logger.info(f"  Starting cleaning for Policy: {policy_num}")
    files = [
        f
        for f in os.listdir(raw_policy_dir)
        if os.path.isfile(os.path.join(raw_policy_dir, f))
    ]
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
                logger.info(f"    Overwriting existing {file}")
            else:
                logger.info(f"    Skipping {file} (Already processed)")
                continue
        success = False
        for attempt in range(3):
            structured_json = process_file(
                raw_filepath, cleaned_filepath, file, policy_num
            )
            if structured_json:
                results_to_save.append((expected_json_path, structured_json))
                success = True
                break
            elif attempt < 2:
                logger.info(f"    Retrying {file}... (Attempt {attempt + 2}/3)")
                time.sleep(2)
        if not success:
            logger.info(
                f"    Failed to process {file} after 3 attempts. Aborting policy {policy_num} to prevent inconsistencies..."
            )
            if os.path.exists(cleaned_policy_dir):
                try:
                    shutil.rmtree(cleaned_policy_dir)
                except Exception as e:
                    logger.info(f"    Could not delete {cleaned_policy_dir}: {e}")
            return
    if results_to_save:
        os.makedirs(cleaned_policy_dir, exist_ok=True)
        for expected_json_path, structured_json in results_to_save:
            with open(expected_json_path, "w", encoding="utf-8") as f:
                f.write(structured_json)
            logger.info(f"    Saved cleaned JSON to {expected_json_path}")
    logger.info(f"  Finished cleaning for Policy: {policy_num}")


def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    raw_dir = os.path.join(base_dir, "interactions_data", "raw")
    cleaned_dir = os.path.join(base_dir, "interactions_data", "cleaned")
    if not os.path.exists(raw_dir):
        logger.info(f"Raw directory not found at {raw_dir}")
        play_sound("error")
        return
    logger.info("Scanning raw directory for policy folders...")
    policy_folders = [
        f for f in os.listdir(raw_dir) if os.path.isdir(os.path.join(raw_dir, f))
    ]
    logger.info(f"Found {len(policy_folders)} policy folders to process.")
    if TEST_MODE:
        logger.info("TEST_MODE is enabled. Only processing 2 policy folders.")
        policy_folders = policy_folders[:2]
    total_to_process = len(policy_folders)
    logger.info(f"Processing {total_to_process} policies SEQUENTIALLY...")
    pipeline_successful = True
    for index, policy_num in enumerate(policy_folders):
        try:
            logger.info(
                f"\nProcessing Policy {index + 1}/{total_to_process}: {policy_num}"
            )
            raw_policy_dir = os.path.join(raw_dir, policy_num)
            cleaned_policy_dir = os.path.join(cleaned_dir, policy_num)
            if not OVERWRITE_EXISTING and os.path.exists(cleaned_policy_dir):
                raw_files_count = len(
                    [
                        f
                        for f in os.listdir(raw_policy_dir)
                        if os.path.isfile(os.path.join(raw_policy_dir, f))
                    ]
                )
                cleaned_files_count = len(
                    [f for f in os.listdir(cleaned_policy_dir) if f.endswith(".json")]
                )
                if cleaned_files_count >= raw_files_count and raw_files_count > 0:
                    logger.info(
                        f"Skipping Policy {policy_num} (Already completely processed in cleaned folder)"
                    )
                    continue
            process_policy_folder(policy_num, raw_policy_dir, cleaned_policy_dir)
            if index < total_to_process - 1:
                delay = random.randint(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
                logger.info(
                    f"  -> Successfully processed. Waiting for {delay} seconds before the next policy..."
                )
                time.sleep(delay)
        except Exception as e:
            logger.info(
                f"\n[!] ERROR OCCURRED during processing policy '{policy_num}':"
            )
            traceback.print_exc()
            logger.info("Stopping the pipeline and sounding alarm...")
            pipeline_successful = False
            play_sound("error")
            break
    logger.info("\nCleaning pipeline finished!")
    if pipeline_successful and total_to_process > 0:
        logger.info("  -> All policies processed! Playing success chime...")
        play_sound("success")


if __name__ == "__main__":
    main()
