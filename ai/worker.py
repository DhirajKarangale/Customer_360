import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

import sys
import time
import redis
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - AI WORKER - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

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
        user_query = payload.get("query") or payload.get("user_query")
        customers_id = payload.get("customers_id")
        insurance_agents_id = payload.get("insurance_agents_id")
        policies_id = payload.get("policies_id")
        
        # Keep backwards compatibility for DB context if needed
        agent_id = insurance_agents_id or payload.get("insurance_agent_id")
        
        logger.info(f"🚀 Job Received | ID: {job_id} | Agent: {agent_id} | Customer: {customers_id} | Policy: {policies_id}")

        db_context = ""
        if agent_id:
            logger.info(f"🔍 Fetching DB context for agent {agent_id}...")
            db_context += db_access.get_agent_context(agent_id) + "\n"
            db_context += db_access.get_customers_for_agent(agent_id) + "\n"

        logger.info(f"📚 Retrieving RAG context for query...")
        rag_context, _ = rag_pipeline.retrieve_context(user_query)
        
        logger.info(f"=== 📄 RAG CONTEXT ===\n{rag_context}\n======================")

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
        
        logger.info(f"🧠 Generating LLM response...")
        llm = get_llm('TRANSCRIPT')
        chain = prompt | llm | StrOutputParser()
        
        response = chain.invoke({
            "db_context": db_context,
            "rag_context": rag_context,
            "user_input": user_query
        })
        
        logger.info(f"=== 🤖 AI RESPONSE ===\n{response}\n======================")
        
        if callback_url:
            logger.info(f"📤 Sending result back to callback URL...")
            callback_data = {
                "job_id": job_id, 
                "message": response
            }
            if customers_id:
                callback_data["customers_id"] = customers_id
            if insurance_agents_id:
                callback_data["insurance_agents_id"] = insurance_agents_id
            if policies_id:
                callback_data["policies_id"] = policies_id
                
            requests.post(callback_url, json=callback_data, timeout=10)
        
        logger.info(f"✅ Job Successfully Completed | ID: {job_id}")
    except Exception as e:
        logger.error(f"❌ Job Failed | ID: {job_id} | Error: {str(e)}")
        if callback_url:
            try:
                requests.post(callback_url, json={"job_id": job_id, "message": f"Error: {e}"}, timeout=10)
            except:
                pass
    finally:
        redis_client.xack(STREAM_KEY, GROUP_NAME, job_id)

def start_worker():
    logger.info("🚀 Starting AI worker... Initialization sequence initiated.")
    db_access = AIDatabaseAccess()
    get_snowflake_conn()
    
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True, health_check_interval=30)
    try:
        redis_client.xgroup_create(STREAM_KEY, GROUP_NAME, id="0", mkstream=True)
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            logger.warning(f"Redis group message: {e}")
            
    rag_pipeline = RAGRetrievalPipeline()
    
    logger.info("🟢 AI worker fully initialized and waiting for jobs...")
    while True:
        try:
            streams = redis_client.xreadgroup(
                GROUP_NAME, CONSUMER_NAME, {STREAM_KEY: ">"}, count=1, block=5000
            )
            if streams:
                for stream, messages in streams:
                    for job_id, payload in messages:
                        process_job(redis_client, job_id, payload, db_access, rag_pipeline)
        except redis.exceptions.ConnectionError:
            logger.warning("⚠️ Redis connection lost. Reconnecting in 5 seconds...")
            time.sleep(5)
            redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True, health_check_interval=30)
        except redis.exceptions.TimeoutError:
            pass
        except Exception as e:
            logger.error(f"💥 Unexpected error in worker loop: {e}")
            time.sleep(1)

if __name__ == "__main__":
    start_worker()
