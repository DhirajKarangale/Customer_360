import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import sys
import time
import redis
import requests

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ai.db.db_access import AIDatabaseAccess
from ai.rag.scripts.retrieval import RAGRetrievalPipeline
from ai.utils.llm_utils import get_llm
from ai.utils.sf_auth import get_snowflake_conn
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
STREAM_KEY = "ai_jobs"
GROUP_NAME = "ai_workers"
CONSUMER_NAME = f"worker-{os.getpid()}"

def process_job(redis_client, job_id, payload, db_access, rag_pipeline):
    callback_url = payload.get("callback_url")
    try:
        user_query = payload.get("user_query")
        agent_id = payload.get("insurance_agent_id")

        db_context = ""
        if agent_id:
            db_context += db_access.get_agent_context(agent_id) + "\n"
            db_context += db_access.get_customers_for_agent(agent_id) + "\n"

        rag_context, _ = rag_pipeline.retrieve_context(user_query)

        prompt_template = """You are a helpful customer support assistant.
Answer the user's query using ONLY the context provided below.

Structured Context:
{db_context}

Unstructured Context:
{rag_context}

User Query:
{user_input}

Answer:"""
        prompt = PromptTemplate.from_template(prompt_template)
        
        llm = get_llm('TRANSCRIPT')
        chain = prompt | llm | StrOutputParser()
        
        response = chain.invoke({
            "db_context": db_context,
            "rag_context": rag_context,
            "user_input": user_query
        })
        
        if callback_url:
            requests.post(callback_url, json={"job_id": job_id, "message": response}, timeout=10)
        
    except Exception as e:
        print(f"Error processing job {job_id}: {e}")
        if callback_url:
            try:
                requests.post(callback_url, json={"job_id": job_id, "message": f"Error: {e}"}, timeout=10)
            except:
                pass
    finally:
        redis_client.xack(STREAM_KEY, GROUP_NAME, job_id)

def start_worker():
    print("Starting AI worker...")
    db_access = AIDatabaseAccess()
    get_snowflake_conn()
    
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    try:
        redis_client.xgroup_create(STREAM_KEY, GROUP_NAME, id="0", mkstream=True)
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            print(f"Redis group error: {e}")
            
    rag_pipeline = RAGRetrievalPipeline()
    
    print("AI worker started, waiting for jobs...")
    while True:
        try:
            streams = redis_client.xreadgroup(
                GROUP_NAME, CONSUMER_NAME, {STREAM_KEY: ">"}, count=1, block=0
            )
            if streams:
                for stream, messages in streams:
                    for job_id, payload in messages:
                        process_job(redis_client, job_id, payload, db_access, rag_pipeline)
        except redis.exceptions.ConnectionError:
            print("Redis connection lost. Reconnecting...")
            time.sleep(5)
            redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        except Exception as e:
            print(f"Unexpected error in worker loop: {e}")
            time.sleep(1)

if __name__ == "__main__":
    start_worker()
