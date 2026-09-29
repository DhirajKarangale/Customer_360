import os
import sys
import time
import subprocess
import re
import json
import threading
from dotenv import load_dotenv

# Load env variables from .env
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(base_dir, ".env")
load_dotenv(env_path)

# Rotate through GROQ_API_KEY0 to GROQ_API_KEY7 (8 keys)
groq_keys = [os.environ.get(f"GROQ_API_KEY{i}") for i in range(8)]
# Rotate through GEMINI_API_KEY0 to GEMINI_API_KEY6 (7 keys)
gemini_keys = [os.environ.get(f"GEMINI_API_KEY{i}") for i in range(7)]

# State variables
groq_key_idx = 0
groq_model_idx = 0
dead_groq_keys = set()

gemini_key_idx = 0
dead_gemini_keys = set()

def save_pending_keys():
    """Saves the keys that are not exhausted so they can be reused later."""
    pending_groq = []
    for i in range(8):
        if i not in dead_groq_keys and groq_keys[i]:
            pending_groq.append(f"GROQ_API_KEY{i}")
            
    pending_gemini = []
    for i in range(7):
        if i not in dead_gemini_keys and gemini_keys[i]:
            pending_gemini.append(f"GEMINI_API_KEY{i}")
            
    out_file = os.path.join(base_dir, "pending_keys.json")
    with open(out_file, "w") as f:
        json.dump({
            "pending_groq_keys": pending_groq,
            "pending_gemini_keys": pending_gemini
        }, f, indent=2)
    print(f"\n[Orchestrator] Saved pending (usable) keys to {out_file}")

def patch_llm_utils(provider, groq_index, gemini_index):
    """
    Temporarily patches utils/llm_utils.py so we don't need to rewrite 
    the actual logic of the existing scripts.
    """
    file_path = os.path.join(base_dir, "utils", "llm_utils.py")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if provider:
        content = re.sub(r'LLM_PROVIDER\s*=\s*".*"', f'LLM_PROVIDER = "{provider}"', content)
    if groq_index is not None:
        content = re.sub(r'GROQ_MODEL_INDEX\s*=\s*\d+', f'GROQ_MODEL_INDEX = {groq_index}', content)
    if gemini_index is not None:
        content = re.sub(r'GEMINI_MODEL_INDEX\s*=\s*\d+', f'GEMINI_MODEL_INDEX = {gemini_index}', content)
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

def get_raw_count():
    """Returns the number of policy directories in the raw interactions folder."""
    raw_dir = os.path.join(base_dir, "data_generation", "interactions_data", "raw")
    if not os.path.exists(raw_dir):
        return 0
    return len([name for name in os.listdir(raw_dir) if os.path.isdir(os.path.join(raw_dir, name))])

def get_cleaned_count():
    """Returns the number of policy directories in the cleaned interactions folder."""
    clean_dir = os.path.join(base_dir, "data_generation", "interactions_data", "cleaned")
    if not os.path.exists(clean_dir):
        return 0
    return len([name for name in os.listdir(clean_dir) if os.path.isdir(os.path.join(clean_dir, name))])

def status_monitor():
    while True:
        try:
            raw = get_raw_count()
            clean = get_cleaned_count()
            print(f"\n[STATUS MONITOR] Generated: {raw}/200 | Cleaned: {clean}/200")
            time.sleep(30)
        except Exception:
            time.sleep(30)

def advance_groq_rotation(reason):
    """Handles rotation of Groq keys and model indices."""
    global groq_key_idx, groq_model_idx
    if reason == "success":
        # Rotate model index between 0 and 1 only
        if groq_model_idx == 0:
            groq_model_idx = 1
        else:
            groq_model_idx = 0
            groq_key_idx = (groq_key_idx + 1) % 8
    elif reason == "dead":
        dead_groq_keys.add(groq_key_idx)
        if len(dead_groq_keys) >= 8:
            print("[Orchestrator] ALL GROQ KEYS DEAD/EXHAUSTED! Exiting Groq phase.")
            return False
        # Fallback to the next available key and reset model index
        groq_key_idx = (groq_key_idx + 1) % 8
        groq_model_idx = 0
    return True

def run_task_with_groq(script_path, task_name, target_count=None):
    """Executes a script with Groq rotation and error handling."""
    global groq_key_idx, groq_model_idx
    retries = 0
    
    while True:
        if len(dead_groq_keys) >= 8:
            print("[Orchestrator] ALL GROQ KEYS EXHAUSTED.")
            return False

        # Skip dead keys
        if groq_key_idx in dead_groq_keys:
            groq_key_idx = (groq_key_idx + 1) % 8
            continue

        current_key = groq_keys[groq_key_idx]
        if not current_key:
            print(f"[Orchestrator] GROQ Key {groq_key_idx} is missing from .env. Marking as dead.")
            if not advance_groq_rotation("dead"):
                return False
            continue
            
        patch_llm_utils("groq", groq_model_idx, 0)
        env = os.environ.copy()
        env["GROQ_API_KEY"] = current_key
        
        print(f"\n[Orchestrator] === Starting {task_name} with GROQ Key {groq_key_idx}, Model {groq_model_idx} (Retry {retries}/3) ===")
        
        process = subprocess.Popen(
            [sys.executable, script_path],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=base_dir
        )
        
        failed = False
        hard_error = False
        
        while True:
            line = process.stdout.readline()
            if not line:
                if process.poll() is not None:
                    break
                continue
            
            sys.stdout.write(line)
            sys.stdout.flush()
            
            # Detect failures that don't crash the script but ruin the output
            fail_indicators = [
                "ERROR OCCURRED", "Traceback", "Content Generation Failed", 
                "Aborted to prevent inconsistencies", "Failed to process", 
                "Could not connect to Snowflake"
            ]
            if any(ind in line for ind in fail_indicators):
                failed = True
                
            # Detect rate limits / hard expirations
            err_keywords = ["rate limit", "exhausted", "quota", "hard expiration", "insufficient_quota"]
            if any(k in line.lower() for k in err_keywords):
                failed = True
                hard_error = True
                
            # Monitor output folder exactly for the 200 items target
            if target_count and get_raw_count() >= target_count:
                print(f"\n[Orchestrator] Target count {target_count} reached! Terminating {task_name}.")
                process.terminate()
                process.wait()
                advance_groq_rotation("success")
                return True
                
            if failed:
                print(f"\n[Orchestrator] Detected failure in output. Terminating process to retry/rotate...")
                process.terminate()
                break
                
        process.wait()
        
        if not failed and process.returncode == 0:
            print(f"\n[Orchestrator] {task_name} successfully completed.")
            advance_groq_rotation("success")
            return True
            
        if hard_error:
            print(f"\n[Orchestrator] Hard expiration/rate limit detected for Key {groq_key_idx}. Marking as dead/exhausted.")
            if not advance_groq_rotation("dead"):
                return False
            retries = 0
        else:
            retries += 1
            if retries >= 3:
                print(f"\n[Orchestrator] {task_name} failed 3 times. Exhausted Key {groq_key_idx}. Falling back to next key.")
                if not advance_groq_rotation("dead"):
                    return False
                retries = 0
            else:
                print(f"\n[Orchestrator] Retrying {task_name}... ({retries}/3)")
                time.sleep(2)

def advance_gemini_rotation(reason):
    """Handles rotation of Gemini keys."""
    global gemini_key_idx
    if reason == "success":
        gemini_key_idx = (gemini_key_idx + 1) % 7
    elif reason == "dead":
        dead_gemini_keys.add(gemini_key_idx)
        if len(dead_gemini_keys) >= 7:
            print("[Orchestrator] ALL GEMINI KEYS DEAD/EXHAUSTED! Exiting Gemini phase.")
            return False
        gemini_key_idx = (gemini_key_idx + 1) % 7
    return True

def run_task_with_gemini(script_path, task_name, target_count=None):
    """Executes a script with Gemini rotation and error handling."""
    global gemini_key_idx
    retries = 0
    
    while True:
        if len(dead_gemini_keys) >= 7:
            print("[Orchestrator] ALL GEMINI KEYS EXHAUSTED.")
            return False

        if gemini_key_idx in dead_gemini_keys:
            gemini_key_idx = (gemini_key_idx + 1) % 7
            continue

        current_key = gemini_keys[gemini_key_idx]
        if not current_key:
            print(f"[Orchestrator] GEMINI Key {gemini_key_idx} is missing from .env. Marking as dead.")
            if not advance_gemini_rotation("dead"):
                return False
            continue
            
        # Set LLM_PROVIDER = "gemini" and model index constant to 0 (gemini-3.5-flash-lite)
        patch_llm_utils("gemini", groq_index=0, gemini_index=0)
        env = os.environ.copy()
        env["GEMINI_API_KEY"] = current_key
        
        print(f"\n[Orchestrator] === Starting {task_name} with GEMINI Key {gemini_key_idx} (Retry {retries}/3) ===")
        
        process = subprocess.Popen(
            [sys.executable, script_path],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=base_dir
        )
        
        failed = False
        hard_error = False
        
        while True:
            line = process.stdout.readline()
            if not line:
                if process.poll() is not None:
                    break
                continue
            
            sys.stdout.write(line)
            sys.stdout.flush()
            
            fail_indicators = [
                "ERROR OCCURRED", "Traceback", "Content Generation Failed", 
                "Aborted to prevent inconsistencies", "Failed to process", 
                "Could not connect to Snowflake"
            ]
            if any(ind in line for ind in fail_indicators):
                failed = True
                
            err_keywords = ["rate limit", "exhausted", "quota", "hard expiration", "insufficient_quota"]
            if any(k in line.lower() for k in err_keywords):
                failed = True
                hard_error = True
                
            if target_count and get_raw_count() >= target_count:
                print(f"\n[Orchestrator] Target count {target_count} reached! Terminating {task_name}.")
                process.terminate()
                process.wait()
                advance_gemini_rotation("success")
                return True
                
            if failed:
                print(f"\n[Orchestrator] Detected failure in output. Terminating process to retry/rotate...")
                process.terminate()
                break
                
        process.wait()
        
        if not failed and process.returncode == 0:
            print(f"\n[Orchestrator] {task_name} successfully completed.")
            advance_gemini_rotation("success")
            return True
            
        if hard_error:
            print(f"\n[Orchestrator] Hard expiration/rate limit detected for Key {gemini_key_idx}. Marking as dead/exhausted.")
            if not advance_gemini_rotation("dead"):
                return False
            retries = 0
        else:
            retries += 1
            if retries >= 3:
                print(f"\n[Orchestrator] {task_name} failed 3 times. Exhausted Key {gemini_key_idx}. Falling back to next key.")
                if not advance_gemini_rotation("dead"):
                    return False
                retries = 0
            else:
                print(f"\n[Orchestrator] Retrying {task_name}... ({retries}/3)")
                time.sleep(2)

def main():
    threading.Thread(target=status_monitor, daemon=True).start()
    gen_script_path = os.path.join(base_dir, "data_generation", "scripts", "generate_interactions_seq.py")
    clean_script_path = os.path.join(base_dir, "data_generation", "scripts", "clean_interactions_seq.py")
    
    try:
        print("\n" + "="*50)
        print("SKIPPING PHASE 1 (GROQ) - Jump straight to Gemini")
        print("="*50)
        
        # success = run_task_with_groq(gen_script_path, "Groq Generation", target_count=200)
        # if not success:
        #     print("[Orchestrator] Groq Generation failed completely.")
            
        # print("\n" + "="*50)
        # print("PHASE 1: GROQ DATA CLEANING")
        # print("="*50)
        # success = run_task_with_groq(clean_script_path, "Groq Cleaning")
        # if not success:
        #     print("[Orchestrator] Groq Cleaning failed completely.")
            
        print("\n" + "="*50)
        print("PHASE 2: GEMINI EXECUTION (Generation & Cleaning)")
        print("="*50)
        success = run_task_with_gemini(gen_script_path, "Gemini Generation", target_count=None)
        if not success:
            print("[Orchestrator] Gemini Generation failed completely.")
            
        print("\n" + "="*50)
        print("PHASE 2: GEMINI CLEANING")
        print("="*50)
        success = run_task_with_gemini(clean_script_path, "Gemini Cleaning")
        if not success:
            print("[Orchestrator] Gemini Cleaning failed completely.")
            
        print("\n[Orchestrator] All phases completed successfully.")
        
    except KeyboardInterrupt:
        print("\n[Orchestrator] Script interrupted by user!")
    finally:
        save_pending_keys()

if __name__ == "__main__":
    main()
