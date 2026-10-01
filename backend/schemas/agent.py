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
