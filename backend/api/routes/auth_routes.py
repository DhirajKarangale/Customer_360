from fastapi import APIRouter, Depends
from backend.schemas.auth import LoginRequest
from backend.schemas.agent import AgentResponse
from backend.services.auth_service import AuthService
from backend.api.dependencies import get_auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=AgentResponse)
def login(request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.authenticate_agent(request)
