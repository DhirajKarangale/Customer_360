from pydantic import BaseModel
from typing import Optional

class AgentResponse(BaseModel):
    id: str
    name: str
    email: str
    phone_number: Optional[str] = None
    agency_name: Optional[str] = None
    license_number: Optional[str] = None
    profile_image_url: Optional[str] = None

class SuggestionsResponse(BaseModel):
    status: str
    message: str
    job_id: Optional[str] = None
    action_text: Optional[str] = None
    last_updated: Optional[str] = None

class SuggestionsCallbackRequest(BaseModel):
    job_id: str
    agent_id: str
    action_text: str
