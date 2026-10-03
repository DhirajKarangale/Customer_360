from fastapi import APIRouter, Depends
from backend.schemas.llm import LLMRequest, LLMResponse, CallbackRequest
from backend.services.llm_service import LLMService
from backend.services.agent_service import AgentService
from backend.services.chat_service import ChatService
from backend.services.sse_manager import sse_manager
from backend.api.dependencies import (
    get_llm_service,
    get_agent_service,
    get_chat_service,
    verify_jwt,
)
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/llm", tags=["LLM Operations"])


@router.post("/generate", response_model=LLMResponse)
def generate_llm_response(
    request: LLMRequest,
    llm_service: LLMService = Depends(get_llm_service),
    chat_service: ChatService = Depends(get_chat_service),
    token_data: dict = Depends(verify_jwt),
):
    import time

    response = llm_service.submit_job(request)
    if not (request.job_id and request.job_id.startswith("suggestion_")):
        agent_id = token_data.get("insurance_agent_id")
        send_time = int(time.time() * 1000)
        chat_service.add_chat(
            response.job_id,
            agent_id,
            request.customers_id,
            request.policies_id,
            request.query,
            send_time,
        )
    return response


@router.post("/callback")
def llm_callback(
    request: CallbackRequest,
    llm_service: LLMService = Depends(get_llm_service),
    agent_service: AgentService = Depends(get_agent_service),
    chat_service: ChatService = Depends(get_chat_service),
):

    if request.insurance_agents_id:
        message_payload = {"job_id": request.job_id, "message": request.message}
        sse_manager.publish(request.insurance_agents_id, message_payload)

    if not (request.job_id and request.job_id.startswith("suggestion_")):
        chat_service.update_chat(request.job_id, request.message)

    if (
        request.job_id
        and request.job_id.startswith("suggestion_")
        and request.insurance_agents_id
    ):
        error_keywords = [
            "apologize",
            "unable to process",
            "system access restrictions",
            "error:",
        ]
        is_error = any(kw in request.message.lower() for kw in error_keywords)

        if not is_error:
            agent_service.agent_repo.update_suggestions(
                request.insurance_agents_id, request.message
            )
        else:
            logger.warning(
                f" LLM Error detected for suggestions. Not saving to DB: {request.message}"
            )

    return {"status": "success"}
