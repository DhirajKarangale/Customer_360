from fastapi import APIRouter, Depends
from backend.schemas.agent import AgentResponse, SuggestionsResponse, SuggestionsCallbackRequest
from backend.services.agent_service import AgentService
from backend.api.dependencies import get_agent_service

router = APIRouter(prefix="/agents", tags=["Insurance Agents"])

from fastapi import Request

@router.get("/{insurance_agent_id}", response_model=AgentResponse)
def get_agent(insurance_agent_id: str, request: Request, agent_service: AgentService = Depends(get_agent_service)):
    base_url = str(request.base_url).rstrip('/')
    return agent_service.get_agent_info(insurance_agent_id, base_url)

@router.get("/{insurance_agent_id}/suggestions", response_model=SuggestionsResponse)
def get_suggestions(insurance_agent_id: str, agent_service: AgentService = Depends(get_agent_service)):
    return agent_service.get_suggestions(insurance_agent_id)

@router.post("/suggestions/callback")
def suggestions_callback(request_data: SuggestionsCallbackRequest, agent_service: AgentService = Depends(get_agent_service)):
    return agent_service.process_suggestions_callback(request_data)
