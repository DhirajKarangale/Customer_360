import os
import sys
import time
import logging
import requests
import redis
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ai.utils.sf_auth import get_snowflake_conn
from ai.agent.workflows import run_suggestions_workflow, run_general_workflow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - AI WORKER - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


REDIS_URL = os.getenv("REDIS_URL")
STREAM_KEY = "ai_jobs"
GROUP_NAME = "ai_workers"


CONSUMER_NAME = "worker-primary"


RECLAIM_EVERY_N_LOOPS = 6
RECLAIM_IDLE_MS = 30_000


def process_job(redis_client, redis_msg_id, payload):
    callback_url = payload.get("callback_url")
    job_id = payload.get("job_id") or redis_msg_id

    logger.info(f"Job Received | ID: {job_id} (Redis Msg: {redis_msg_id})")

    try:
        if job_id.startswith("suggestion_"):
            response = run_suggestions_workflow(payload)
        else:
            response = run_general_workflow(payload)

        if callback_url:
            logger.info(f"Sending result back to callback URL... (ID: {job_id})")
            callback_data = {
                "job_id": job_id,
                "message": response,
                "insurance_agents_id": payload.get("insurance_agents_id"),
            }
            requests.post(callback_url, json=callback_data, timeout=10)

        logger.info(f"Job Successfully Completed | ID: {job_id}")
    except Exception as e:
        logger.error(f"Job Failed | ID: {job_id} | Error: {str(e)}")
        if callback_url:
            try:
                requests.post(
                    callback_url,
                    json={"job_id": job_id, "message": f"Error: {e}"},
                    timeout=10,
                )
            except Exception:
                pass
    finally:

        try:
            redis_client.xack(STREAM_KEY, GROUP_NAME, redis_msg_id)
        except Exception as ack_err:
            logger.warning(f"Failed to xack message {redis_msg_id}: {ack_err}")


def _do_reclaim(redis_client, min_idle_ms: int, label: str = "") -> int:
    """
    Core reclaim logic. Tries xautoclaim (Redis 7+), falls back to
    xpending_range + xclaim for older Redis.
    Returns number of messages reclaimed.
    """
    try:
        result = redis_client.xautoclaim(
            STREAM_KEY,
            GROUP_NAME,
            CONSUMER_NAME,
            min_idle_time=min_idle_ms,
            start_id="0-0",
            count=100,
        )
        claimed_messages = result[1] if result and len(result) > 1 else []
        if claimed_messages:
            for msg_id, payload in claimed_messages:
                process_job(redis_client, msg_id, payload)
        return len(claimed_messages)
    except (redis.exceptions.ResponseError, AttributeError):

        return _reclaim_fallback(redis_client, min_idle_ms, label)
    except Exception as e:
        logger.warning(f"Reclaim failed: {e}")
        return 0


def _reclaim_fallback(redis_client, min_idle_ms: int, label: str = "") -> int:
    """xpending_range + xclaim fallback for Redis < 7.0."""
    count = 0
    try:
        pending_msgs = redis_client.xpending_range(
            STREAM_KEY, GROUP_NAME, "-", "+", count=100
        )
        for msg_info in pending_msgs:
            if msg_info.get("time_since_delivered", 0) < min_idle_ms:
                continue
            msg_id = msg_info["message_id"]
            try:
                claimed = redis_client.xclaim(
                    STREAM_KEY,
                    GROUP_NAME,
                    CONSUMER_NAME,
                    min_idle_time=min_idle_ms,
                    message_ids=[msg_id],
                )
                for claimed_id, payload in claimed:
                    process_job(redis_client, claimed_id, payload)
                    count += 1
            except Exception as e:
                logger.warning(f"Could not claim {msg_id}: {e}")
    except Exception as e:
        logger.warning(f"Fallback reclaim failed: {e}")
    return count


def startup_reclaim(redis_client):
    """
    On startup: claim ALL pending messages from any previous crash (idle >= 0ms).
    Runs once before entering the main loop.
    """
    _do_reclaim(redis_client, min_idle_ms=0, label="[startup] ")


def periodic_reclaim(redis_client):
    """
    Periodic check: only reclaim messages idle > RECLAIM_IDLE_MS.
    This catches jobs where a previous worker died mid-processing while this
    worker was already running (so startup_reclaim didn't catch it).
    """
    _do_reclaim(redis_client, min_idle_ms=RECLAIM_IDLE_MS, label="[periodic] ")


def start_worker():
    get_snowflake_conn()

    redis_client = redis.Redis.from_url(
        REDIS_URL, decode_responses=True, health_check_interval=30
    )

    try:
        redis_client.xgroup_create(STREAM_KEY, GROUP_NAME, id="$", mkstream=True)
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            logger.warning(f"Redis group message: {e}")

    startup_reclaim(redis_client)

    loop_count = 0
    while True:
        try:
            streams = redis_client.xreadgroup(
                GROUP_NAME, CONSUMER_NAME, {STREAM_KEY: ">"}, count=1, block=5000
            )
            if streams:
                for _, messages in streams:
                    for job_id, payload in messages:
                        process_job(redis_client, job_id, payload)

            loop_count += 1
            if loop_count % RECLAIM_EVERY_N_LOOPS == 0:
                periodic_reclaim(redis_client)

        except redis.exceptions.ConnectionError:
            logger.warning("Redis connection lost. Reconnecting in 5 seconds...")
            time.sleep(5)
            redis_client = redis.Redis.from_url(
                REDIS_URL, decode_responses=True, health_check_interval=30
            )
            loop_count = 0
        except redis.exceptions.TimeoutError:
            pass
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Unexpected error in worker loop: {e}")
            time.sleep(1)


if __name__ == "__main__":
    start_worker()
