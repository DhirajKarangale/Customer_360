import os
import uuid
import redis
from fastapi import HTTPException, status
from backend.schemas.llm import LLMRequest, LLMResponse

class LLMService:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

    def submit_job(self, request: LLMRequest) -> LLMResponse:
        try:
            job_id = str(uuid.uuid4())
            callback = request.callback_url or "http://localhost:8000/api/v1/llm/callback"
            
            payload = {
                "job_id": job_id,
                "query": request.query,
                "callback_url": callback
            }
            if request.customers_id:
                payload["customers_id"] = request.customers_id
            if request.insurance_agents_id:
                payload["insurance_agents_id"] = request.insurance_agents_id
            if request.policies_id:
                payload["policies_id"] = request.policies_id
            
            self.redis_client.xadd("ai_jobs", payload)
            
            return LLMResponse(status="job_submitted", job_id=job_id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Redis Error: {str(e)}")
