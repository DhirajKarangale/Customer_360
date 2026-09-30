from fastapi import APIRouter, Depends
from backend.schemas.llm import LLMRequest, LLMResponse, CallbackRequest
from backend.services.llm_service import LLMService
from backend.api.dependencies import get_llm_service
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
    llm_service: LLMService = Depends(get_llm_service)
):
    logger.info(f"Received callback for job {request.job_id}: {request.message[:50]}...")
    return {"status": "success"}
