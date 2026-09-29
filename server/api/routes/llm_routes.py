from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from server.schemas.llm import LLMRequest
from server.services.llm_service import LLMService
from server.api.dependencies import get_llm_service

router = APIRouter(prefix="/llm", tags=["LLM Operations"])

@router.post("/generate", response_class=PlainTextResponse)
def generate_llm_response(
    request: LLMRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    return llm_service.generate_response(request)
