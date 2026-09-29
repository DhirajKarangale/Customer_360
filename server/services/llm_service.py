import sys
import os
from fastapi import HTTPException, status
from server.schemas.llm import LLMRequest, LLMResponse

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.llm_utils import get_llm

class LLMService:
    def generate_response(self, request: LLMRequest) -> LLMResponse:
        try:
            llm_runnable = get_llm(request.model_key)
            if not llm_runnable:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="LLM configuration error")
            
            result = llm_runnable.invoke(request.prompt)
            if hasattr(result, "content"):
                result_str = result.content
            else:
                result_str = str(result)
                
            return LLMResponse(response=result_str)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"LLM Error: {str(e)}")
