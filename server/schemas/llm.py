from pydantic import BaseModel
from typing import Optional

class LLMRequest(BaseModel):
    query: str
    id: Optional[str] = None
