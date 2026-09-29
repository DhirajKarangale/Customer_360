from fastapi import APIRouter, Depends
from server.schemas.auth import LoginRequest
from server.schemas.agent import AgentResponse
from server.services.auth_service import AuthService
from server.api.dependencies import get_auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=AgentResponse)
def login(request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.authenticate_agent(request)
