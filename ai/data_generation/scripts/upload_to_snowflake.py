import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ai.utils.sf_auth import get_snowflake_conn
import concurrent.futures
import threading
OVERRIDE_DUPLICATE_FILES = False
MAX_WORKERS = 8
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
if not os.path.exists(env_path):
    raise FileNotFoundError(f'Environment file not found at {env_path}')
load_dotenv(env_path)
stats_lock = threading.Lock()
upload_count = 0
skip_count = 0
override_count = 0

def process_file(file_info, sf_conn, stage_name):
    global upload_count, skip_count, override_count
    local_path, stage_relative_path, folder, policy_num, is_duplicate = file_info
    if is_duplicate and (not OVERRIDE_DUPLICATE_FILES):
        print(f'  [SKIPPED] {stage_relative_path} (already present)')
        with stats_lock:
            skip_count += 1
        return
    put_path = local_path.replace('\\', '/')
    cursor = sf_conn.cursor()
    try:
        overwrite_flag = 'TRUE' if is_duplicate and OVERRIDE_DUPLICATE_FILES else 'FALSE'
        query = f"PUT 'file://{put_path}' @{stage_name}/{folder}/{policy_num} AUTO_COMPRESS=FALSE OVERWRITE={overwrite_flag}"
        cursor.execute(query)
        if is_duplicate and OVERRIDE_DUPLICATE_FILES:
            print(f'  [OVERWRITTEN] {stage_relative_path}')
            with stats_lock:
                override_count += 1
        else:
            print(f'  [UPLOADED] {stage_relative_path}')
            with stats_lock:
                upload_count += 1
    except Exception as e:
        print(f'  [ERROR] Failed to upload {local_path}: {e}')
    finally:
        cursor.close()

def main():
    print('Connecting to Snowflake...')
    try:
        sf_conn = get_snowflake_conn()
    except Exception as e:
        print(f'Could not connect to Snowflake: {e}')
        return
    cursor = sf_conn.cursor()
    stage_name = 'INTERACTIONS_STAGE'
    cursor.execute(f'CREATE STAGE IF NOT EXISTS {stage_name}')
    print(f"Stage '{stage_name}' is ready.")
    print('Checking for existing files in the Snowflake stage...')
    existing_files = set()
    try:
        cursor.execute(f'LIST @{stage_name}')
        for row in cursor.fetchall():
            file_path = row[0]
            if file_path.lower().startswith(f'{stage_name.lower()}/'):
                file_path = file_path[len(stage_name) + 1:]
            existing_files.add(file_path)
    except Exception as e:
        print(f'Warning: Could not list stage (it might be empty): {e}')
    finally:
        cursor.close()
    base_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'interactions_data')
    folders_to_upload = ['raw', 'cleaned']
    print('Scanning local directory and queueing files for upload...')
    total_files_on_snowflake = len(existing_files)
    print(f'Total files initially present on Snowflake: {total_files_on_snowflake}')
    all_files_to_process = []
    for folder in folders_to_upload:
        data_dir = os.path.join(base_data_dir, folder)
        if not os.path.exists(data_dir):
            continue
        for root, dirs, files in os.walk(data_dir):
            policy_num = os.path.basename(root)
            if policy_num in ['interactions_data', 'raw', 'cleaned', '']:
                continue
            for file in files:
                local_path = os.path.join(root, file)
                stage_relative_path = f'{folder}/{policy_num}/{file}'
                is_duplicate = stage_relative_path in existing_files or f'{stage_relative_path}.gz' in existing_files
                all_files_to_process.append((local_path, stage_relative_path, folder, policy_num, is_duplicate))
    print(f'Starting parallel upload process using {MAX_WORKERS} workers...')
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for file_info in all_files_to_process:
            futures.append(executor.submit(process_file, file_info, sf_conn, stage_name))
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f'Worker encountered an error: {e}')
    sf_conn.close()
    total_files_after_upload = total_files_on_snowflake + upload_count
    print('\n--- Upload Summary ---')
    print(f'Total files initially present on Snowflake: {total_files_on_snowflake}')
    print(f'New files uploaded: {upload_count}')
    print(f'Duplicate files overwritten: {override_count}')
    print(f'Duplicate files ignored (skipped): {skip_count}')
    print(f'Total files in Snowflake after upload: {total_files_after_upload}')
    print('Upload process complete!')
if __name__ == '__main__':
    main()