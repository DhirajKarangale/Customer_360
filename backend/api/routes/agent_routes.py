from fastapi import APIRouter, Depends
from backend.schemas.agent import AgentResponse
from backend.services.agent_service import AgentService
from backend.api.dependencies import get_agent_service

router = APIRouter(prefix="/agents", tags=["Insurance Agents"])

@router.get("/{insurance_agent_id}", response_model=AgentResponse)
def get_agent(insurance_agent_id: str, agent_service: AgentService = Depends(get_agent_service)):
    return agent_service.get_agent_info(insurance_agent_id)
