from typing import Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from ai.db.db_access import AIDatabaseAccess
from ai.rag.scripts.retrieval import RAGRetrievalPipeline
from ai.rag.config import SIMILARITY_SCORE_THRESHOLD

class SearchInput(BaseModel):
    query: str = Field(description="The search query to find in the documents.")
    policy_id: Optional[str] = Field(default=None, description="The specific policy ID to filter by, if applicable.")
    customer_id: Optional[str] = Field(default=None, description="The specific customer ID or name to filter by, if applicable.")
    agent_id: Optional[str] = Field(default=None, description="The specific agent ID or name to filter by, if applicable.")

@tool("search_unstructured_interactions", args_schema=SearchInput)
def search_unstructured_interactions(query: str, policy_id: Optional[str] = None, customer_id: Optional[str] = None, agent_id: Optional[str] = None) -> str:
    """Search transcripts, chats, and emails for relevant context. Provide a policy_id, customer_id, or agent_id to strongly filter the results."""
    import uuid
    def is_uuid(val: str) -> bool:
        try:
            uuid.UUID(val)
            return True
        except ValueError:
            return False

    db = AIDatabaseAccess()
    try:
        import ai.agent.state
        from ai.agent.restrictions import restriction_manager
        
        logged_in_agent_id = ai.agent.state.CURRENT_AGENT_ID
        is_allowed, error_msg = restriction_manager.check_access(
            db_access=db,
            logged_in_agent_id=logged_in_agent_id,
            target_agent_identifier=agent_id,
            target_customer_identifier=customer_id,
            target_policy_identifier=policy_id
        )
        if not is_allowed:
            return error_msg

        if policy_id and policy_id not in query:
            query = f"{query} {policy_id}"
            
        if customer_id:
            if is_uuid(customer_id):
                # Fetch name to boost FAISS recall and fix metadata ID mismatches
                c_details = db.get_customer_details(customer_id)
                import re
                name_match = re.search(r"Structured Customer Details for (.*?):", c_details)
                if name_match:
                    name = name_match.group(1).strip()
                    if name not in query:
                        query = f"{query} {name}"
                    customer_id = name # overwrite to use name for filtering!
            elif customer_id not in query:
                query = f"{query} {customer_id}"
                
        if agent_id:
            if is_uuid(agent_id):
                a_details = db.get_agent_context(agent_id)
                import re
                name_match = re.search(r"Agent Name: (.*?),", a_details)
                if name_match:
                    name = name_match.group(1).strip()
                    if name not in query:
                        query = f"{query} {name}"
                    agent_id = name # overwrite to use name for filtering!
            elif agent_id not in query:
                query = f"{query} {agent_id}"
    finally:
        db.close()
        
    rag_pipeline = RAGRetrievalPipeline()
    try:
        query_embedding = rag_pipeline._embedder.embed_text(query)
        # Increase top_k if any filters are applied to ensure we don't miss them before Python filtering
        has_filter = policy_id or customer_id or agent_id
        results = rag_pipeline._vector_store.similarity_search(
            query_embedding,
            top_k=100 if has_filter else 10,
            score_threshold=0.0 if has_filter else SIMILARITY_SCORE_THRESHOLD
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
            c_name = participants.get("customer", {}).get("name", "Unknown")
            c_id = participants.get("customer", {}).get("id", "Unknown")
            
            if customer_id and customer_id not in c_name and customer_id != c_id:
                continue
                
            agents = participants.get("insurance_agents", [])
            a_names = [a.get("name", "Unknown") for a in agents]
            a_ids = [a.get("id", "Unknown") for a in agents]
            
            if agent_id:
                agent_match = False
                for an, aid in zip(a_names, a_ids):
                    if agent_id in an or agent_id == aid:
                        agent_match = True
                        break
                if not agent_match:
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
            return "No relevant context found after applying filters."
            
        return "\n".join(formatted_context[:5])
    finally:
        rag_pipeline.close()

class DatabaseInput(BaseModel):
    agent_id: Optional[str] = Field(default=None, description="The agent ID to fetch context for.")
    policy_id: Optional[str] = Field(default=None, description="The policy ID to fetch structured policy details for (e.g. premium, coverage).")
    customer_id: Optional[str] = Field(default=None, description="The customer ID or customer name to fetch exact structured details for (e.g. phone number, DOB, address).")

@tool("get_database_context", args_schema=DatabaseInput)
def get_database_context(agent_id: Optional[str] = None, policy_id: Optional[str] = None, customer_id: Optional[str] = None) -> str:
    """Fetch structured customer, agent, or policy details from the PostgreSQL database using their respective ID or name."""
    if not agent_id and not policy_id and not customer_id:
        return "No agent ID, policy ID, or customer ID provided."
        
    db_access = AIDatabaseAccess()
    try:
        import ai.agent.state
        from ai.agent.restrictions import restriction_manager
        
        logged_in_agent_id = ai.agent.state.CURRENT_AGENT_ID
        is_allowed, error_msg = restriction_manager.check_access(
            db_access=db_access,
            logged_in_agent_id=logged_in_agent_id,
            target_agent_identifier=agent_id,
            target_customer_identifier=customer_id,
            target_policy_identifier=policy_id
        )
        if not is_allowed:
            return error_msg
            
        db_context = ""
        if customer_id:
            db_context += db_access.get_customer_details(customer_id) + "\n"
        if policy_id:
            db_context += db_access.get_policy_details(policy_id) + "\n"
        if agent_id:
            db_context += db_access.get_agent_context(agent_id) + "\n"
            db_context += db_access.get_customers_for_agent(agent_id) + "\n"
            
        return db_context
    except Exception as e:
        return f"Error connecting to database: {e}"
    finally:
        db_access.close()

class SQLQueryInput(BaseModel):
    query: str = Field(description="The exact PostgreSQL query to execute. MUST be read-only (SELECT).")

@tool("execute_sql_query", args_schema=SQLQueryInput)
def execute_sql_query(query: str) -> str:
    """Execute a raw PostgreSQL query to answer complex or aggregated questions about customers, policies, agents, or customer_interactions."""
    import ai.agent.state
    from ai.agent.restrictions import restriction_manager
    
    logged_in_agent_id = ai.agent.state.CURRENT_AGENT_ID
    
    if restriction_manager.enabled and logged_in_agent_id:
        # Schema queries are safe and shouldn't require the agent ID
        is_schema_query = "information_schema" in query.lower() or "pg_catalog" in query.lower()
        if not is_schema_query and logged_in_agent_id not in query:
            return "SYSTEM ERROR: ACCESS DENIED. (AI INSTRUCTION: CRITICAL: DO NOT RETRY. You attempted to access data without filtering by your agent ID. Stop immediately and politely inform the user that you can only access their own policies, customers, and data.)"
            
    db_access = AIDatabaseAccess()
    try:
        res = db_access.execute_query(query)
        if restriction_manager.enabled and logged_in_agent_id and ("Query returned no results" in res or res.strip() == ""):
             return "SYSTEM ERROR: NO RESULTS FOUND. (AI INSTRUCTION: CRITICAL: DO NOT RETRY. The data doesn't exist or belongs to someone else. Stop immediately.)"
        return res
    except Exception as e:
        return f"Error executing query: {e}"
    finally:
        db_access.close()

TOOLS = [search_unstructured_interactions, get_database_context, execute_sql_query]
