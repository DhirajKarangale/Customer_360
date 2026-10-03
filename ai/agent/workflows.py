import logging
from ai.agent.run import invoke_agent
import concurrent.futures
from ai.agent.memory import fetch_and_filter_memory, update_redis_memory_background

logger = logging.getLogger(__name__)

def run_suggestions_workflow(payload: dict) -> str:
    """
    Workflow for generating suggestions for an insurance agent.
    """
    agent_id = payload.get("insurance_agents_id") or payload.get("agent_id")
    logger.info(f"🧠 Running LangGraph Agent for suggestions (Agent ID: {agent_id})...")
    
    system_query = "Analyze my recent customer interactions and expiring policies to generate 3 actionable suggestions for today. Format as a clean list and explain why."
    
    response_html, response_raw = invoke_agent(
        user_query=system_query,
        insurance_agents_id=agent_id
    )
    return response_html

def run_general_workflow(payload: dict) -> str:
    """
    Workflow for generic agent invocations from the frontend LLM chat.
    """
    user_query = payload.get("query") or payload.get("user_query")
    customers_id = payload.get("customers_id")
    insurance_agents_id = payload.get("insurance_agents_id")
    policies_id = payload.get("policies_id")

    logger.info(f"🧠 Running LangGraph Agent for general query...")
    
    # Run query operations AND memory retrieval at the EXACT same time (parallely)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        memory_future = executor.submit(fetch_and_filter_memory, user_query, insurance_agents_id)
        # You could submit other parallel operations here
        
        memory_messages = memory_future.result()

    response_html, response_raw = invoke_agent(
        user_query=user_query,
        customers_id=customers_id,
        insurance_agents_id=insurance_agents_id,
        policies_id=policies_id,
        memory_messages=memory_messages
    )
    
    # Fire and forget the memory update in the background (does not block)
    update_redis_memory_background(insurance_agents_id, user_query, response_raw)
    
    return response_html
