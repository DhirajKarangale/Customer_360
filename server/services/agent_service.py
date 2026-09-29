from fastapi import HTTPException, status
from server.db.repositories.agent_repo import AgentRepository
from server.schemas.agent import AgentResponse

class AgentService:
    def __init__(self, agent_repo: AgentRepository):
        self.agent_repo = agent_repo

    def get_agent_info(self, agent_id: str) -> AgentResponse:
        agent = self.agent_repo.get_agent_by_id(agent_id)
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        
        return AgentResponse(
            id=str(agent.get("ID") or agent.get("id")),
            name=agent.get("NAME") or agent.get("name"),
            email=agent.get("EMAIL") or agent.get("email"),
            phone_number=agent.get("PHONE_NUMBER") or agent.get("phone_number"),
            agency_name=agent.get("AGENCY_NAME") or agent.get("agency_name"),
            license_number=agent.get("LICENSE_NUMBER") or agent.get("license_number"),
        )
