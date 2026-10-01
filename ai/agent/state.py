from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# Global variable to hold the logged-in agent ID securely for tools
# This is safe because the AI worker processes jobs sequentially in a single thread.
CURRENT_AGENT_ID = None

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    customers_id: str | None
    insurance_agents_id: str | None
    policies_id: str | None
