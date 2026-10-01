import os
import uuid
import redis
from fastapi import HTTPException, status
from backend.schemas.llm import LLMRequest, LLMResponse

class LLMService:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL")
        self.redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

    def submit_job(self, request: LLMRequest) -> LLMResponse:
        try:
            job_id = str(uuid.uuid4())
            default_callback = os.getenv("CALLBACK_URL")
            callback = request.callback_url or default_callback
            
            final_query = request.query
            if request.insurance_agents_id and request.insurance_agents_id not in final_query:
                final_query += f" {request.insurance_agents_id}"
            if request.customers_id and request.customers_id not in final_query:
                final_query += f" {request.customers_id}"
            if request.policies_id and request.policies_id not in final_query:
                final_query += f" {request.policies_id}"
                
            payload = {
                "job_id": job_id,
                "query": final_query,
                "callback_url": callback
            }
            if request.insurance_agents_id:
                payload["insurance_agents_id"] = request.insurance_agents_id
            
            self.redis_client.xadd("ai_jobs", payload)
            
            return LLMResponse(status="job_submitted", job_id=job_id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Redis Error: {str(e)}")
