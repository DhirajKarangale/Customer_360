from pydantic import BaseModel
from typing import Optional

class LLMRequest(BaseModel):
    query: str
    id: Optional[str] = None
    insurance_agent_id: Optional[str] = None
    callback_url: Optional[str] = None

class LLMResponse(BaseModel):
    status: str
    job_id: str

class CallbackRequest(BaseModel):
    job_id: str
    message: str
