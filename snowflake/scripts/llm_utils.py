import os
from google import genai
from groq import Groq
from sf_auth import get_snowflake_conn

# 'snowflake', 'gemini', or 'groq'
LLM_PROVIDER = "gemini"

GEMINI_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash"
]

GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b"
]

GEMINI_MODEL_INDEX = 3
GROQ_MODEL_INDEX = 0
CORTEX_CALL_COUNT = 0
CURRENT_CONN = None

def _call_snowflake_llm(sf_conn, prompt, model_name):
    global CORTEX_CALL_COUNT, CURRENT_CONN
    
    # Initialize CURRENT_CONN with the one passed from main on first run
    if CURRENT_CONN is None:
        CURRENT_CONN = sf_conn
        
    CORTEX_CALL_COUNT += 1
    
    if CORTEX_CALL_COUNT % 7 == 0:
        print(f"    [Auth] Reached {CORTEX_CALL_COUNT} LLM calls. Refreshing Snowflake connection...")
        try:
            CURRENT_CONN.close()
        except Exception:
            pass
        CURRENT_CONN = get_snowflake_conn()

    conn_to_use = CURRENT_CONN
    cursor = conn_to_use.cursor()
    query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model_name}', %s)"
    try:
        cursor.execute(query, (prompt,))
        result = cursor.fetchone()[0]
        return result
    except Exception as e:
        print(f"Error calling Cortex: {e}")
        if "Session no longer exists" in str(e):
            print("    [Auth] Session expired! Force refreshing connection and retrying...")
            try:
                conn_to_use.close()
            except Exception:
                pass
            CURRENT_CONN = get_snowflake_conn()
            conn_to_use = CURRENT_CONN
            cursor = conn_to_use.cursor()
            try:
                cursor.execute(query, (prompt,))
                result = cursor.fetchone()[0]
                return result
            except Exception as e2:
                print(f"Retry failed: {e2}")
                return None
        else:
            return None
    finally:
        try:
            cursor.close()
        except Exception:
            pass

def _call_gemini_llm(prompt, model_name):
    try:
        gemini_model = GEMINI_MODELS[GEMINI_MODEL_INDEX]
    except IndexError:
        gemini_model = GEMINI_MODELS[0]
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found in environment variables.")
        return None
        
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.generate_content(
            model=gemini_model,
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return None

def _call_groq_llm(prompt, model_name):
    try:
        groq_model = GROQ_MODELS[GROQ_MODEL_INDEX]
    except IndexError:
        groq_model = GROQ_MODELS[0]
        
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("GROQ_API_KEY not found in environment variables.")
        return None
        
    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=groq_model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error calling Groq: {e}")
        return None

def call_llm(sf_conn, prompt, model_name):
    """
    General function to call the configured LLM provider.
    """
    if LLM_PROVIDER.lower() == "snowflake":
        return _call_snowflake_llm(sf_conn, prompt, model_name)
    elif LLM_PROVIDER.lower() == "gemini":
        return _call_gemini_llm(prompt, model_name)
    elif LLM_PROVIDER.lower() == "groq":
        return _call_groq_llm(prompt, model_name)
    else:
        print(f"Unknown LLM provider: {LLM_PROVIDER}")
        return None
