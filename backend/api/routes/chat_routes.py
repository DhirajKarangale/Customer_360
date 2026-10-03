from fastapi import APIRouter, Depends
from backend.services.chat_service import ChatService
from backend.api.dependencies import get_chat_service, verify_jwt

router = APIRouter(prefix="/chats", tags=["Chats"])


@router.get("/")
def get_all_chats(
    token_data: dict = Depends(verify_jwt),
    chat_service: ChatService = Depends(get_chat_service),
):
    agent_id = token_data.get("insurance_agent_id")
    if not agent_id:
        return []
    return chat_service.get_all_chats(agent_id)


@router.delete("/")
def clear_chats(
    token_data: dict = Depends(verify_jwt),
    chat_service: ChatService = Depends(get_chat_service),
):
    agent_id = token_data.get("insurance_agent_id")
    if agent_id:
        chat_service.clear_chats(agent_id)
    return {"status": "success"}
