import os
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from utils.sf_auth import get_snowflake_conn

LLM_PROVIDER = 'gemini'
SNOWFLAKE_MODELS = {'SEQUENCE': 'llama3.1-8b', 'TRANSCRIPT': 'llama3.1-70b', 'SUMMARY': 'llama3.1-8b', 'CLEANING': 'llama3.1-70b', 'STRUCTURING': 'llama3.1-70b', 'EMBEDDING': 'snowflake-arctic-embed-l-v2.0'}
GEMINI_MODELS = ['gemini-3.5-flash-lite', 'gemini-3.1-pro-preview', 'gemini-3.5-flash', 'gemini-3.6-flash', 'gemini-3.7-flash', 'gemini-3.8-flash']
GROQ_MODELS = ['openai/gpt-oss-120b', 'qwen/qwen3.8-27b', 'openai/gpt-oss-20b']
GEMINI_MODEL_INDEX = 0
GROQ_MODEL_INDEX = 0
CORTEX_CALL_COUNT = 0

def _get_snowflake_llm(model_name):

    def call_snowflake(prompt) -> str:
        if hasattr(prompt, 'to_string'):
            prompt_str = prompt.to_string()
        elif isinstance(prompt, list) and len(prompt) > 0 and hasattr(prompt[0], 'content'):
            prompt_str = prompt[0].content
        elif hasattr(prompt, 'content'):
            prompt_str = prompt.content
        else:
            prompt_str = str(prompt)
        global CORTEX_CALL_COUNT
        conn_to_use = get_snowflake_conn()
        CORTEX_CALL_COUNT += 1
        if CORTEX_CALL_COUNT % 7 == 0:
            print(f'    [Auth] Reached {CORTEX_CALL_COUNT} LLM calls. Refreshing Snowflake connection...')
            conn_to_use = get_snowflake_conn(force_refresh=True)
        cursor = conn_to_use.cursor()
        query = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model_name}', %s)"
        try:
            cursor.execute(query, (prompt_str,))
            result = cursor.fetchone()[0]
            return result
        except Exception as e:
            print(f'Error calling Cortex: {e}')
            if 'Session no longer exists' in str(e):
                print('    [Auth] Session expired! Force refreshing connection and retrying...')
                conn_to_use = get_snowflake_conn(force_refresh=True)
                cursor = conn_to_use.cursor()
                try:
                    cursor.execute(query, (prompt_str,))
                    result = cursor.fetchone()[0]
                    return result
                except Exception as e2:
                    print(f'Retry failed: {e2}')
                    return None
            else:
                return None
        finally:
            try:
                cursor.close()
            except Exception:
                pass
    return RunnableLambda(call_snowflake)

def _get_gemini_llm(model_name=None):
    try:
        gemini_model = GEMINI_MODELS[GEMINI_MODEL_INDEX]
    except IndexError:
        gemini_model = GEMINI_MODELS[0]
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print('GEMINI_API_KEY not found in environment variables.')
        return None
    return ChatGoogleGenerativeAI(model=gemini_model, google_api_key=api_key)

def _get_groq_llm(model_name=None):
    try:
        groq_model = GROQ_MODELS[GROQ_MODEL_INDEX]
    except IndexError:
        groq_model = GROQ_MODELS[0]
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print('GROQ_API_KEY not found in environment variables.')
        return None
    return ChatGroq(model_name=groq_model, groq_api_key=api_key)

def get_llm(model_key):
    if model_key not in SNOWFLAKE_MODELS:
        raise ValueError(f"Model key '{model_key}' not found in SNOWFLAKE_MODELS.")
    if LLM_PROVIDER.lower() == 'snowflake':
        actual_model = SNOWFLAKE_MODELS[model_key]
        return _get_snowflake_llm(actual_model)
    elif LLM_PROVIDER.lower() == 'gemini':
        return _get_gemini_llm(model_key)
    elif LLM_PROVIDER.lower() == 'groq':
        return _get_groq_llm(model_key)
    else:
        print(f'Unknown LLM provider: {LLM_PROVIDER}')
        return None

def get_snowflake_embedding(text: str, model_key: str, dimension: int) -> list[float]:
    if model_key not in SNOWFLAKE_MODELS:
        raise ValueError(f"Model key '{model_key}' not found in SNOWFLAKE_MODELS.")
    actual_model = SNOWFLAKE_MODELS[model_key]
    global CORTEX_CALL_COUNT
    conn_to_use = get_snowflake_conn()
    CORTEX_CALL_COUNT += 1
    if CORTEX_CALL_COUNT % 7 == 0:
        print(f'    [Auth] Reached {CORTEX_CALL_COUNT} LLM calls. Refreshing Snowflake connection...')
        conn_to_use = get_snowflake_conn(force_refresh=True)
    query = f'SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_{dimension}(%s, %s)'
    cursor = conn_to_use.cursor()
    try:
        cursor.execute(query, (actual_model, text))
        result = cursor.fetchone()[0]
        import json
        if isinstance(result, list):
            return [float(x) for x in result]
        if isinstance(result, str):
            parsed = json.loads(result)
            return [float(x) for x in parsed]
        return [float(x) for x in result]
    except Exception as e:
        print(f'Error calling Cortex Embedding: {e}')
        if 'Session no longer exists' in str(e) or 'session' in str(e).lower():
            print('    [Auth] Session expired! Force refreshing connection and retrying...')
            conn_to_use = get_snowflake_conn(force_refresh=True)
            cursor = conn_to_use.cursor()
            try:
                cursor.execute(query, (actual_model, text))
                result = cursor.fetchone()[0]
                import json
                if isinstance(result, list):
                    return [float(x) for x in result]
                if isinstance(result, str):
                    parsed = json.loads(result)
                    return [float(x) for x in parsed]
                return [float(x) for x in result]
            except Exception as e2:
                print(f'Retry failed: {e2}')
                raise e2
        else:
            raise
    finally:
        try:
            cursor.close()
        except Exception:
            pass