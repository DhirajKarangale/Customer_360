from fastapi import APIRouter, Depends, Request, HTTPException, status
from backend.schemas.auth import LoginRequest, LoginResponse
from backend.schemas.agent import AgentResponse
from backend.services.auth_service import AuthService
from backend.services.agent_service import AgentService
from backend.api.dependencies import get_auth_service, get_agent_service, verify_jwt

router = APIRouter(prefix="/auth", tags=["Authentication"])

from fastapi import Request

@router.post("/login", response_model=LoginResponse)
def login(request_data: LoginRequest, request: Request, auth_service: AuthService = Depends(get_auth_service)):
    base_url = str(request.base_url).rstrip('/')
    return auth_service.authenticate_agent(request_data, base_url)

@router.get("/verify", response_model=AgentResponse)
def verify(request: Request, token_data: dict = Depends(verify_jwt), agent_service: AgentService = Depends(get_agent_service)):
    base_url = str(request.base_url).rstrip('/')
    agent_id = token_data.get("insurance_agent_id")
    if not agent_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    return agent_service.get_agent_info(agent_id, base_url)

from fastapi.responses import FileResponse, RedirectResponse
import tempfile
import os

@router.get("/images/{filename}")
def get_profile_image(filename: str):
    try:
        import sys
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from ai.utils.sf_auth import get_snowflake_conn
        
        # Download from Snowflake
        tmp_dir = tempfile.gettempdir()
        dest_path = os.path.join(tmp_dir, filename)
        
        if not os.path.exists(dest_path):
            sf_conn = get_snowflake_conn()
            cursor = sf_conn.cursor()
            tmp_uri = tmp_dir.replace('\\', '/')
            cursor.execute(f"GET @PROFILE_IMAGES_STAGE/{filename} 'file://{tmp_uri}'")
            cursor.close()
            
        if os.path.exists(dest_path):
            return FileResponse(dest_path)
    except Exception as e:
        # If Snowflake fails (e.g. stage doesn't exist, no auth, module missing), fallback to a beautiful generated avatar
        seed = filename.split('.')[0]
        fallback_url = f"https://api.dicebear.com/7.x/avataaars/png?seed={seed}&backgroundColor=b6e3f4,c0aede,d1d4f9,ffdfbf"
        return RedirectResponse(url=fallback_url)
        
    return {"error": "Image not found"}
