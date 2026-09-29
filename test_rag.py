import os
import sys
from dotenv import load_dotenv

# Ensure the root directory is in sys.path so modules can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from rag.scripts.retrieval import RAGRetrievalPipeline
from utils.llm_utils import get_llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def main():
    # Load environment variables
    load_dotenv()
    
    # 1. Hardcoded user input
    user_input = "Can you give me an overview of recent customer complaints regarding cancelled policies?"
    
    print(f"User Input:\n{user_input}\n")
    print("=" * 60)
    
    # 2. Call the RAG retrieval pipeline
    print("Retrieving context from RAG pipeline...")
    retrieval_pipeline = RAGRetrievalPipeline()
    try:
        context, count = retrieval_pipeline.retrieve_context(user_input)
    finally:
        retrieval_pipeline.close()
        
    print(f"\nRetrieved Context Count: {count}")
    # print("\nRetrieved Context:")
    # print(context)
    print("=" * 60)
    
    # 3 & 4. Setup LLM prompt and call LLM using only utils/llm_utils.py
    prompt_template = """You are an intelligent customer support assistant.
Answer the user's query using ONLY the context provided below. Be precise and directly answer the question asked.
If the answer is not contained in the context, say "I don't have enough information to answer that."

Context:
{context}

User Query:
{user_input}

Answer:"""
    
    prompt = PromptTemplate.from_template(prompt_template)
    
    print("\nInitializing LLM...")
    # 'TRANSCRIPT' uses llama3.1-70b (or Groq/Gemini depending on config)
    llm = get_llm('TRANSCRIPT') 
    
    if not llm:
        print("Error: Could not initialize LLM.")
        return
        
    chain = prompt | llm | StrOutputParser()
    
    print("Generating response...")
    print("=" * 60)
    
    # 5. Log the LLM response clearly
    try:
        response = chain.invoke({
            "context": context,
            "user_input": user_input
        })
        print("\n[LLM Response]:")
        print(response)
    except Exception as e:
        print(f"Error calling LLM: {e}")

if __name__ == "__main__":
    main()
