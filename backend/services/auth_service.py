from fastapi import HTTPException, status
from backend.schemas.auth import LoginRequest
from backend.schemas.agent import AgentResponse
from backend.db.repositories.agent_repo import AgentRepository
import hashlib

class AuthService:
    def __init__(self, agent_repo: AgentRepository):
        self.agent_repo = agent_repo

    def authenticate_agent(self, login_data: LoginRequest) -> AgentResponse:
        error_msg = "Invalid email or password. Please double-check your credentials and try again."
        
        agent = self.agent_repo.get_agent_by_email(login_data.email)
        
        if not agent:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_msg)
        
        db_password = agent.get("PASSWORD") or agent.get("password")
        
        if db_password is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_msg)
            
        hashed_input = hashlib.sha256(login_data.password.encode('utf-8')).hexdigest()
        
        if hashed_input != db_password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_msg)
        
        agent_data = AgentResponse(
            id=str(agent.get("ID") or agent.get("id")),
            name=agent.get("NAME") or agent.get("name"),
            email=agent.get("EMAIL") or agent.get("email"),
            phone_number=agent.get("PHONE_NUMBER") or agent.get("phone_number"),
            agency_name=agent.get("AGENCY_NAME") or agent.get("agency_name"),
            license_number=agent.get("LICENSE_NUMBER") or agent.get("license_number"),
        )
        
        return agent_data
