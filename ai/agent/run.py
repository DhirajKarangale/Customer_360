from ai.agent.graph import agent_app
from langchain_core.messages import HumanMessage
import logging

logger = logging.getLogger(__name__)

def invoke_agent(user_query: str, customers_id: str = None, insurance_agents_id: str = None, policies_id: str = None) -> str:
    """
    Invokes the LangGraph agent with the user's query.
    Returns the final response string.
    """
    inputs = {
        "messages": [HumanMessage(content=user_query)],
        "customers_id": customers_id,
        "insurance_agents_id": insurance_agents_id,
        "policies_id": policies_id
    }
    
    try:
        # recursion_limit=15 prevents infinite loops if the LLM gets stuck
        final_state = agent_app.invoke(inputs, {"recursion_limit": 15})
        
        # The final message should be the AI's response
        final_message = final_state["messages"][-1]
        return final_message.content
        
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return f"I encountered an error while processing your request: {e}"
