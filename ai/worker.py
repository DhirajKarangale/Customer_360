import os
import sys
import time
import logging
import requests
import redis
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ai.utils.sf_auth import get_snowflake_conn
from ai.agent.workflows import run_suggestions_workflow, run_general_workflow

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - AI WORKER - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
STREAM_KEY = "ai_jobs"
GROUP_NAME = "ai_workers"
CONSUMER_NAME = f"worker-{os.getpid()}"


def process_job(redis_client, redis_msg_id, payload):
    callback_url = payload.get("callback_url")
    job_id = payload.get("job_id") or redis_msg_id
    
    logger.info(f"🚀 Job Received | ID: {job_id} (Redis Msg: {redis_msg_id})")
    logger.info(f"📦 Incoming Payload: {payload}")

    try:
        if job_id.startswith("suggestion_"):
            response = run_suggestions_workflow(payload)
            logger.info(f"=== 🤖 AI SUGGESTIONS RESPONSE ===\n{response}\n======================")
        else:
            response = run_general_workflow(payload)
            logger.info(f"=== 🤖 AI RESPONSE ===\n{response}\n======================")

        if callback_url:
            logger.info(f"📤 Sending result back to callback URL...")
            callback_data = {
                "job_id": job_id,
                "message": response,
                "insurance_agents_id": payload.get("insurance_agents_id")
            }
            logger.info(f"📦 Outgoing Callback Payload: {callback_data}")
            requests.post(callback_url, json=callback_data, timeout=10)

        logger.info(f"✅ Job Successfully Completed | ID: {job_id}")
    except Exception as e:
        logger.error(f"❌ Job Failed | ID: {job_id} | Error: {str(e)}")
        if callback_url:
            try:
                requests.post(callback_url, json={
                              "job_id": job_id, "message": f"Error: {e}"}, timeout=10)
            except:
                pass
    finally:
        redis_client.xack(STREAM_KEY, GROUP_NAME, redis_msg_id)


def start_worker():
    logger.info("🚀 Starting AI worker... Initialization sequence initiated.")
    get_snowflake_conn()

    redis_client = redis.Redis.from_url(
        REDIS_URL, decode_responses=True, health_check_interval=30)
    try:
        redis_client.xgroup_create(
            STREAM_KEY, GROUP_NAME, id="0", mkstream=True)
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            logger.warning(f"Redis group message: {e}")

    logger.info("🟢 AI worker fully initialized and waiting for jobs...")
    while True:
        try:
            streams = redis_client.xreadgroup(
                GROUP_NAME, CONSUMER_NAME, {STREAM_KEY: ">"}, count=1, block=5000
            )
            if streams:
                for stream, messages in streams:
                    for job_id, payload in messages:
                        process_job(redis_client, job_id, payload)
        except redis.exceptions.ConnectionError:
            logger.warning(
                "⚠️ Redis connection lost. Reconnecting in 5 seconds...")
            time.sleep(5)
            redis_client = redis.Redis.from_url(
                REDIS_URL, decode_responses=True, health_check_interval=30)
        except redis.exceptions.TimeoutError:
            pass
        except Exception as e:
            logger.error(f"💥 Unexpected error in worker loop: {e}")
            time.sleep(1)


if __name__ == "__main__":
    start_worker()
