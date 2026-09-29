import sys
import os
from fastapi import HTTPException, status
from server.schemas.llm import LLMRequest

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.llm_utils import get_llm
from rag.scripts.retrieval import RAGRetrievalPipeline
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class LLMService:
    def __init__(self):
        pass
        
    def generate_response(self, request: LLMRequest) -> str:
        try:
            # 1. Retrieve context
            retrieval_pipeline = RAGRetrievalPipeline()
            try:
                context, count = retrieval_pipeline.retrieve_context(request.query)
            finally:
                retrieval_pipeline.close()

            # 2. Setup prompt
            prompt_template = """You are a helpful, empathetic, and knowledgeable customer support assistant.
Your goal is to provide a clear, conversational, and easy-to-understand response for a non-technical user, just as a real human would speak to them.
Ensure your response is well-formatted with proper spacing, line breaks, and bullet points if necessary to make it highly readable.

Answer the user's query using ONLY the context provided below. 
If the answer is not contained in the context, politely let the user know that you don't have enough information to answer that.

Context:
{context}

User Query:
{user_input}

Answer:"""
            prompt = PromptTemplate.from_template(prompt_template)
            
            # 3. Get LLM
            llm = get_llm('TRANSCRIPT')
            if not llm:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="LLM configuration error")
                
            chain = prompt | llm | StrOutputParser()
            
            # 4. Generate
            response = chain.invoke({
                "context": context,
                "user_input": request.query
            })
            
            return response
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"LLM Error: {str(e)}")
