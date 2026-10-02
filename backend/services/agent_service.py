from fastapi import HTTPException, status
from backend.db.repositories.agent_repo import AgentRepository
from backend.schemas.agent import AgentResponse, SuggestionsResponse, SuggestionsCallbackRequest
import os
import uuid
import redis
from datetime import datetime, timedelta

class AgentService:
    def __init__(self, agent_repo: AgentRepository):
        self.agent_repo = agent_repo

    def get_agent_info(self, agent_id: str, base_url: str = "http://localhost:8000") -> AgentResponse:
        agent = self.agent_repo.get_agent_by_id(agent_id)
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        
        profile_image_url = agent.get("PROFILE_IMAGE_URL") or agent.get("profile_image_url")
        proxy_url = None
        if profile_image_url:
            parts = profile_image_url.split('/', 1)
            if len(parts) == 2:
                filename = parts[1]
                proxy_url = f"{base_url}/api/v1/auth/images/{filename}"

        return AgentResponse(
            id=str(agent.get("ID") or agent.get("id")),
            name=agent.get("NAME") or agent.get("name"),
            email=agent.get("EMAIL") or agent.get("email"),
            phone_number=agent.get("PHONE_NUMBER") or agent.get("phone_number"),
            agency_name=agent.get("AGENCY_NAME") or agent.get("agency_name"),
            license_number=agent.get("LICENSE_NUMBER") or agent.get("license_number"),
            profile_image_url=proxy_url
        )

    def get_suggestions(self, agent_id: str) -> SuggestionsResponse:
        agent = self.agent_repo.get_agent_by_id(agent_id)
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        
        suggestions_text = agent.get("SUGGESTIONS") or agent.get("suggestions")
        suggestions_updated_at = agent.get("SUGGESTIONS_UPDATED_AT") or agent.get("suggestions_updated_at")
        
        if suggestions_text and suggestions_updated_at:
            if datetime.now() - suggestions_updated_at < timedelta(hours=24):
                return SuggestionsResponse(
                    status="success",
                    message="Found recent suggestions.",
                    action_text=suggestions_text,
                    last_updated=suggestions_updated_at.isoformat()
                )
        
        job_id = f"suggestion-{uuid.uuid4()}"
        
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
            payload = {
                "job_id": job_id,
                "agent_id": agent_id,
                "job_type": "suggestions_generation",
                "callback_url": f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/v1/agents/suggestions/callback"
            }
            redis_client.xadd("ai_jobs", payload)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Redis Error: {str(e)}")
            
        return SuggestionsResponse(
            status="pending",
            message="Analyzing your recent interactions and policies to generate your personalized suggestions for today. This will just take a moment.",
            job_id=job_id
        )

    def process_suggestions_callback(self, callback_data: SuggestionsCallbackRequest) -> dict:
        self.agent_repo.update_suggestions(callback_data.agent_id, callback_data.action_text)
        return {"status": "success"}
