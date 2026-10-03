import os
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from ai.utils.sf_auth import get_snowflake_conn
LLM_PROVIDERS_LIST = ['gemini', 'groq', 'snowflake']

# ─── Snowflake Cortex Model Assignments ────────────────────────────────────────
# Model names must be lowercase kebab-case as used by SNOWFLAKE.CORTEX.COMPLETE().
# Source catalog: 'snowflake models.csv' (SHOW CORTEX BASE MODELS output).
#
# Each key maps to a list: [primary_model, fallback1, fallback2, ...]
# Index 0 is always tried first. On any failure, the next model is tried in order.
# Order: best → good → fast-but-always-available (Llama 3.x as last resort).
SNOWFLAKE_MODELS = {
    # ── TRANSCRIPT: Main agent — reasoning, tool-call JSON, final responses ──────
    # Primary: claude-sonnet-4-5 — best instruction following & agentic accuracy.
    'TRANSCRIPT':   ['claude-sonnet-4-5',  'llama4-maverick',  'llama3.3-70b',   'llama3.1-70b'],

    # ── RESTRICTION: Security entity extraction (JSON) from the user query ───────
    # Primary: llama4-maverick — high-end MoE, fast + accurate JSON extraction.
    'RESTRICTION':  ['llama4-maverick',    'llama4-scout',     'llama3.3-70b',   'llama3.1-8b'],

    # ── FORMAT: HTML tag wrapping only — no reasoning needed ────────────────────
    # Primary: gemini-2.5-flash — fastest high-quality model for reformatting.
    'FORMAT':       ['gemini-2.5-flash',   'llama4-maverick',  'llama4-scout',   'llama3.1-8b'],

    # ── SEQUENCE: Interaction sequence planning (JSON list output) ───────────────
    # Primary: llama4-maverick — consistent, well-formatted JSON at MoE speed.
    'SEQUENCE':     ['llama4-maverick',    'llama4-scout',     'llama3.3-70b',   'llama3.1-8b'],

    # ── SUMMARY: 1-2 sentence summarization of interactions ──────────────────────
    # Primary: gemini-2.5-flash — excellent at concise summarization, very fast.
    'SUMMARY':      ['gemini-2.5-flash',   'llama4-maverick',  'llama4-scout',   'llama3.1-8b'],

    # ── CLEANING: Semantic text normalization, grammar, noise removal ─────────────
    # Primary: llama4-maverick — strong semantic rewriting at high speed.
    'CLEANING':     ['llama4-maverick',    'llama3.3-70b',     'llama3.1-70b'],

    # ── STRUCTURING: Strict JSON extraction for RAG ingestion ────────────────────
    # Primary: claude-sonnet-4-5 — highest schema-compliance accuracy.
    'STRUCTURING':  ['claude-sonnet-4-5',  'llama4-maverick',  'llama3.3-70b',   'llama3.1-70b'],

    # ── EMBEDDING: Semantic vector embeddings for FAISS store ────────────────────
    # Single model — no fallback needed (embedding dimension must stay consistent).
    'EMBEDDING':    ['snowflake-arctic-embed-l-v2.0'],
}
GEMINI_MODELS = ['gemini-3.5-flash-lite', 'gemini-3.1-pro-preview',
                 'gemini-3.5-flash', 'gemini-3.6-flash', 'gemini-3.7-flash', 'gemini-3.8-flash']
GROQ_MODELS = ['openai/gpt-oss-120b', 'qwen/qwen3.8-27b', 'openai/gpt-oss-20b']
GEMINI_MODEL_INDEX = 0
GROQ_MODEL_INDEX = 0
CORTEX_CALL_COUNT = 0


def _parse_keys(env_var_name: str) -> list:
    val = os.getenv(env_var_name, '')
    cleaned = val.replace('\n', ',').replace('"', '').replace("'", "")
    return [k.strip() for k in cleaned.split(',') if k.strip()]


def _call_snowflake_direct(prompt_str: str, model_name: str) -> str:
    global CORTEX_CALL_COUNT
    conn_to_use = get_snowflake_conn()
    CORTEX_CALL_COUNT += 1
    if CORTEX_CALL_COUNT % 7 == 0:
        print(
            f'    [Auth] Reached {CORTEX_CALL_COUNT} LLM calls. Refreshing Snowflake connection...')
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
            print(
                '    [Auth] Session expired! Force refreshing connection and retrying...')
            conn_to_use = get_snowflake_conn(force_refresh=True)
            cursor = conn_to_use.cursor()
            try:
                cursor.execute(query, (prompt_str,))
                result = cursor.fetchone()[0]
                return result
            except Exception as e2:
                print(f'Retry failed: {e2}')
                return None
        raise e
    finally:
        try:
            cursor.close()
        except Exception:
            pass


def _extract_prompt_str(prompt) -> str:
    if hasattr(prompt, 'to_string'):
        return prompt.to_string()
    elif isinstance(prompt, list) and len(prompt) > 0 and hasattr(prompt[0], 'content'):
        return prompt[0].content
    elif hasattr(prompt, 'content'):
        return prompt.content
    else:
        return str(prompt)


def _unified_llm_call(prompt_str: str, model_key: str) -> str:
    for provider in LLM_PROVIDERS_LIST:
        print(f"Using LLM Provider: {provider}")

        if provider == 'gemini':
            keys = _parse_keys('GEMINI_API_KEY')
            if not keys:
                print("No Gemini keys found, skipping.")
                continue

            try:
                model_name = GEMINI_MODELS[GEMINI_MODEL_INDEX]
            except IndexError:
                model_name = GEMINI_MODELS[0]

            total_keys = len(keys)
            for idx, key in enumerate(keys, 1):
                print(f"Trying Gemini key {idx}/{total_keys}")
                try:
                    llm = ChatGoogleGenerativeAI(
                        model=model_name, google_api_key=key, temperature=0.0)
                    response = llm.invoke(prompt_str)
                    if isinstance(response.content, list):
                        return "".join([part.get("text", "") for part in response.content if isinstance(part, dict) and "text" in part])
                    return str(response.content)
                except Exception as e:
                    print(f"Error with Gemini key {idx}/{total_keys}: {e}")

        elif provider == 'groq':
            keys = _parse_keys('GROQ_API_KEY')
            if not keys:
                print("No Groq keys found, skipping.")
                continue

            try:
                model_name = GROQ_MODELS[GROQ_MODEL_INDEX]
            except IndexError:
                model_name = GROQ_MODELS[0]

            total_keys = len(keys)
            for idx, key in enumerate(keys, 1):
                print(f"Trying Groq key {idx}/{total_keys}")
                try:
                    llm = ChatGroq(model_name=model_name, groq_api_key=key, temperature=0.0)
                    response = llm.invoke(prompt_str)
                    return response.content
                except Exception as e:
                    print(f"Error with Groq key {idx}/{total_keys}: {e}")

        elif provider == 'snowflake':
            # Index 0 is primary; the rest are fallbacks tried in order.
            models_to_try = SNOWFLAKE_MODELS.get(model_key, [])
            if not models_to_try:
                print(f"Model key '{model_key}' not found in SNOWFLAKE_MODELS.")
                continue

            for model_name in models_to_try:
                print(f"Trying Snowflake model: {model_name}")
                try:
                    result = _call_snowflake_direct(prompt_str, model_name)
                    if result is not None:
                        return result
                    print(f"  Snowflake model '{model_name}' returned None, trying next...")
                except Exception as e:
                    err_str = str(e)
                    print(f"  Snowflake error ({model_name}): {err_str[:120]}")
                    # Unknown model → no point retrying same key, skip to next fallback
                    if 'unknown model' in err_str.lower():
                        continue
                    # Session / auth errors → refresh and try same model once more
                    if 'Session no longer exists' in err_str or 'session' in err_str.lower():
                        try:
                            get_snowflake_conn(force_refresh=True)
                            result = _call_snowflake_direct(prompt_str, model_name)
                            if result is not None:
                                return result
                        except Exception:
                            pass
                    # For any other error, try next fallback model
                    continue

    raise Exception("All LLM providers and model fallbacks exhausted.")



def get_llm(model_key: str, strictly_snowflake: bool = False):
    def llm_executor(prompt):
        prompt_str = _extract_prompt_str(prompt)
        if strictly_snowflake:
            models = SNOWFLAKE_MODELS.get(model_key, [])
            if not models:
                raise ValueError(
                    f"Model key '{model_key}' not found in SNOWFLAKE_MODELS.")
            # strictly_snowflake always uses only the primary (index 0) model.
            return _call_snowflake_direct(prompt_str, models[0])
        else:
            return _unified_llm_call(prompt_str, model_key)

    return RunnableLambda(llm_executor)


def get_snowflake_embedding(text: str, model_key: str, dimension: int) -> list[float]:
    models = SNOWFLAKE_MODELS.get(model_key, [])
    if not models:
        raise ValueError(
            f"Model key '{model_key}' not found in SNOWFLAKE_MODELS.")
    actual_model = models[0]  # Embedding model is always fixed — use primary only.
    global CORTEX_CALL_COUNT
    conn_to_use = get_snowflake_conn()
    CORTEX_CALL_COUNT += 1
    if CORTEX_CALL_COUNT % 7 == 0:
        print(
            f'    [Auth] Reached {CORTEX_CALL_COUNT} LLM calls. Refreshing Snowflake connection...')
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
            print(
                '    [Auth] Session expired! Force refreshing connection and retrying...')
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
