import os
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from utils.sf_auth import get_snowflake_conn

# 'snowflake', 'gemini', or 'groq'
LLM_PROVIDER = "gemini"

GEMINI_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-pro-preview",
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

GEMINI_MODEL_INDEX = 0
GROQ_MODEL_INDEX = 0
CORTEX_CALL_COUNT = 0
CURRENT_CONN = None

def _get_snowflake_chain(model_name):
    """Returns a LangChain RunnableLambda that calls Snowflake Cortex."""
    def call_snowflake(prompt: str) -> str:
        global CORTEX_CALL_COUNT, CURRENT_CONN
        
        if CURRENT_CONN is None:
            CURRENT_CONN = get_snowflake_conn()
            
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
                
    return RunnableLambda(call_snowflake)

def get_llm(model_name=None):
    """
    Returns a LangChain BaseChatModel (for Gemini/Groq) or a RunnableLambda (for Snowflake).
    This allows uniform usage in LangChain/LangGraph pipelines.
    """
    if LLM_PROVIDER.lower() == "snowflake":
        return _get_snowflake_chain(model_name or "llama3.1-70b")
        
    elif LLM_PROVIDER.lower() == "gemini":
        try:
            gemini_model = GEMINI_MODELS[GEMINI_MODEL_INDEX]
        except IndexError:
            gemini_model = GEMINI_MODELS[0]
            
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("GEMINI_API_KEY not found in environment variables.")
            return None
            
        return ChatGoogleGenerativeAI(model=gemini_model, google_api_key=api_key)
        
    elif LLM_PROVIDER.lower() == "groq":
        try:
            groq_model = GROQ_MODELS[GROQ_MODEL_INDEX]
        except IndexError:
            groq_model = GROQ_MODELS[0]
            
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("GROQ_API_KEY not found in environment variables.")
            return None
            
        return ChatGroq(model_name=groq_model, groq_api_key=api_key)
        
    else:
        print(f"Unknown LLM provider: {LLM_PROVIDER}")
        return None

def call_llm(sf_conn, prompt, model_name):
    """
    General function to call the configured LLM provider for simple operations.
    (Preserved for backward compatibility, but uses the unified LangChain approach internally).
    Note: sf_conn is ignored unless CURRENT_CONN is None.
    """
    llm = get_llm(model_name)
    if not llm:
        return None
        
    try:
        # If it's a RunnableLambda (Snowflake), it takes a string and returns a string
        if isinstance(llm, RunnableLambda):
            return llm.invoke(prompt)
        # If it's a BaseChatModel (Gemini/Groq), it takes a string/messages and returns an AIMessage
        else:
            response = llm.invoke([HumanMessage(content=prompt)])
            content = response.content
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, str):
                        text_parts.append(part)
                    elif isinstance(part, dict) and 'text' in part:
                        text_parts.append(part['text'])
                    else:
                        text_parts.append(str(part))
                return "".join(text_parts)
            return content
    except Exception as e:
        print(f"Error calling LLM ({LLM_PROVIDER}): {e}")
        return None
