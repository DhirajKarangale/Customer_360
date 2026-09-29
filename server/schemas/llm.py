from pydantic import BaseModel

class LLMRequest(BaseModel):
    query: str
