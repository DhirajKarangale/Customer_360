from ai.agent.graph import agent_app
from langchain_core.messages import HumanMessage
import logging

logger = logging.getLogger(__name__)


def invoke_agent(
    user_query: str,
    customers_id: str = None,
    insurance_agents_id: str = None,
    policies_id: str = None,
    memory_messages: list = None,
) -> tuple[str, str]:
    """
    Invokes the LangGraph agent with the user's query.
    Returns the final response string.
    """
    messages = []
    if memory_messages:
        messages.extend(memory_messages)
    messages.append(HumanMessage(content=user_query))

    inputs = {
        "messages": messages,
        "customers_id": customers_id,
        "insurance_agents_id": insurance_agents_id,
        "policies_id": policies_id,
    }

    try:

        final_state = agent_app.invoke(inputs, {"recursion_limit": 25})

        messages = final_state["messages"]
        import os

        if os.getenv("ENABLE_TEXT_FORMAT") == "True" and len(messages) >= 2:
            formatted_message = messages[-1].content
            raw_message = messages[-2].content
        else:
            formatted_message = messages[-1].content
            raw_message = messages[-1].content

        return formatted_message, raw_message

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        return (
            f"I encountered an error while processing your request: {e}",
            f"Error: {e}",
        )
