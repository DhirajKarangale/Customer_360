from fastapi import HTTPException, status
from backend.schemas.auth import LoginRequest, LoginResponse
from backend.schemas.agent import AgentResponse
from backend.db.repositories.agent_repo import AgentRepository
from backend.utils.jwt_utils import create_access_token
import hashlib

class AuthService:
    def __init__(self, agent_repo: AgentRepository):
        self.agent_repo = agent_repo

    def authenticate_agent(self, login_data: LoginRequest, base_url: str = "http://localhost:8000") -> LoginResponse:
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
        
        profile_image_url = agent.get("PROFILE_IMAGE_URL") or agent.get("profile_image_url")
        proxy_url = None
        if profile_image_url:
            parts = profile_image_url.split('/', 1)
            if len(parts) == 2:
                filename = parts[1]
                # Return an absolute FastAPI route URL that proxies the image
                proxy_url = f"{base_url}/api/v1/auth/images/{filename}"

        agent_data = AgentResponse(
            id=str(agent.get("ID") or agent.get("id")),
            name=agent.get("NAME") or agent.get("name"),
            email=agent.get("EMAIL") or agent.get("email"),
            phone_number=agent.get("PHONE_NUMBER") or agent.get("phone_number"),
            agency_name=agent.get("AGENCY_NAME") or agent.get("agency_name"),
            license_number=agent.get("LICENSE_NUMBER") or agent.get("license_number"),
            profile_image_url=proxy_url
        )
        
        access_token = create_access_token(data={"insurance_agent_id": agent_data.id})
        
        return LoginResponse(agent_data=agent_data, access_token=access_token)
