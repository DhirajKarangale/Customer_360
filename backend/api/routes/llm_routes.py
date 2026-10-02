from fastapi import APIRouter, Depends
from backend.schemas.llm import LLMRequest, LLMResponse, CallbackRequest
from backend.services.llm_service import LLMService
from backend.services.agent_service import AgentService
from backend.api.dependencies import get_llm_service, get_agent_service
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/llm", tags=["LLM Operations"])

@router.post("/generate", response_model=LLMResponse)
def generate_llm_response(
    request: LLMRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    return llm_service.submit_job(request)

@router.post("/callback")
def llm_callback(
    request: CallbackRequest,
    llm_service: LLMService = Depends(get_llm_service),
    agent_service: AgentService = Depends(get_agent_service)
):
    logger.info(f"Received callback payload: {request.model_dump()}")
    
    if request.job_id.startswith("suggestion_") and request.insurance_agents_id:
        error_keywords = ["apologize", "unable to process", "system access restrictions", "error:"]
        is_error = any(kw in request.message.lower() for kw in error_keywords)
        
        if not is_error:
            agent_service.agent_repo.update_suggestions(request.insurance_agents_id, request.message)
        else:
            logger.warning(f"⚠️ LLM Error detected for suggestions. Not saving to DB: {request.message}")
        
    return {"status": "success"}
