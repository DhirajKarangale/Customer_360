from fastapi import APIRouter, Depends
from backend.schemas.auth import LoginRequest
from backend.schemas.agent import AgentResponse
from backend.services.auth_service import AuthService
from backend.api.dependencies import get_auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

from fastapi import Request

@router.post("/login", response_model=AgentResponse)
def login(request_data: LoginRequest, request: Request, auth_service: AuthService = Depends(get_auth_service)):
    base_url = str(request.base_url).rstrip('/')
    return auth_service.authenticate_agent(request_data, base_url)

from fastapi.responses import FileResponse
import tempfile
import os

@router.get("/images/{filename}")
def get_profile_image(filename: str):
    import sys
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from ai.utils.sf_auth import get_snowflake_conn
    
    # Download from Snowflake
    tmp_dir = tempfile.gettempdir()
    dest_path = os.path.join(tmp_dir, filename)
    
    try:
        if not os.path.exists(dest_path):
            sf_conn = get_snowflake_conn()
            cursor = sf_conn.cursor()
            # GET command automatically decrypts the file when downloaded
            # We must use file://{tmp_dir} as destination
            # Windows path handling for Snowflake GET:
            tmp_uri = tmp_dir.replace('\\', '/')
            cursor.execute(f"GET @PROFILE_IMAGES_STAGE/{filename} 'file://{tmp_uri}'")
            cursor.close()
            
        if os.path.exists(dest_path):
            return FileResponse(dest_path)
        else:
            return {"error": "Image not found"}
    except Exception as e:
        return {"error": str(e)}
