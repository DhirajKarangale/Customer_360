from pydantic import BaseModel, EmailStr
from backend.schemas.agent import AgentResponse

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    agent_data: AgentResponse
    access_token: str
