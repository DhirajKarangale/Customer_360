from typing import Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from ai.db.db_access import AIDatabaseAccess
from ai.rag.scripts.retrieval import RAGRetrievalPipeline
from ai.rag.config import SIMILARITY_SCORE_THRESHOLD

class SearchInput(BaseModel):
    query: str = Field(description="The search query to find in the documents.")
    policy_id: Optional[str] = Field(default=None, description="The specific policy ID to filter by, if applicable.")

@tool("search_unstructured_interactions", args_schema=SearchInput)
def search_unstructured_interactions(query: str, policy_id: Optional[str] = None) -> str:
    """Search transcripts, chats, and emails for relevant context. Provide a policy_id to strongly filter the results for that specific policy."""
    if policy_id and policy_id not in query:
        query = f"{query} {policy_id}"
        
    rag_pipeline = RAGRetrievalPipeline()
    try:
        query_embedding = rag_pipeline._embedder.embed_text(query)
        results = rag_pipeline._vector_store.similarity_search(
            query_embedding,
            top_k=100 if policy_id else 5,
            score_threshold=0.0  # Temporarily lower threshold to ensure we catch the ID
        )
        
        if not results:
            return "No relevant context found."
            
        import re
        formatted_context = []
        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            source_doc = result.get("source_document", "")
            if not source_doc:
                source_doc = metadata.get("source_document", "")
            
            policy_match = re.search(r'POL-\d+-\d+', source_doc)
            doc_policy_number = policy_match.group(0) if policy_match else "Unknown"
            
            if policy_id and policy_id != doc_policy_number:
                continue
                
            participants = metadata.get("participants", {})
            customer_name = participants.get("customer", {}).get("name", "Unknown")
            mood = metadata.get("user_mood", "neutral")
            doc_type = metadata.get("type", "unknown")
            timestamp = metadata.get("timestamp", "unknown")
            topics = metadata.get("topics", [])
            action_items = metadata.get("action_items", [])
            
            doc_str = (
                f"### [Document {i}]\n"
                f"**Policy Number:** {doc_policy_number}\n"
                f"**Type:** {doc_type}\n"
                f"**Date:** {timestamp}\n"
                f"**Customer:** {customer_name} (Mood: {mood})\n"
            )
            if topics:
                doc_str += f"**Topics:** {', '.join(topics)}\n"
            if action_items:
                doc_str += f"**Action Items:** {', '.join(action_items)}\n"
            doc_str += f"**Summary:** {result.get('chunk_text', '')}\n"
            formatted_context.append(doc_str)
            
        if not formatted_context:
            return f"No relevant context found for policy {policy_id}."
            
        return "\n".join(formatted_context[:5])
    finally:
        rag_pipeline.close()

class DatabaseInput(BaseModel):
    agent_id: Optional[str] = Field(default=None, description="The agent ID to fetch context for.")

@tool("get_database_context", args_schema=DatabaseInput)
def get_database_context(agent_id: Optional[str] = None) -> str:
    """Fetch structured customer and agent details from the PostgreSQL database using the agent's ID."""
    if not agent_id:
        return "No agent ID provided."
    db_access = AIDatabaseAccess()
    try:
        db_context = db_access.get_agent_context(agent_id) + "\n"
        db_context += db_access.get_customers_for_agent(agent_id) + "\n"
        return db_context
    except Exception as e:
        return f"Error connecting to database: {e}"
    finally:
        db_access.close()

TOOLS = [search_unstructured_interactions, get_database_context]
