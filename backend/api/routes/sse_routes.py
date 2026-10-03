import asyncio
import json
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from backend.services.sse_manager import sse_manager
from backend.api.dependencies import verify_jwt
from backend.utils.logger import get_logger
logger = get_logger(__name__)
router = APIRouter(prefix="/stream", tags=["SSE"])
@router.get("/")
async def sse_endpoint(request: Request, token_data: dict = Depends(verify_jwt)):
    agent_id = token_data.get("insurance_agent_id")
    if not agent_id:
        return {"error": "Invalid token"}
    queue = await sse_manager.connect(agent_id)
    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        finally:
            sse_manager.disconnect(agent_id, queue)
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )