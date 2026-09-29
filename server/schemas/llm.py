from pydantic import BaseModel

class LLMRequest(BaseModel):
    prompt: str
    model_key: str = "SUMMARY"

class LLMResponse(BaseModel):
    response: str
