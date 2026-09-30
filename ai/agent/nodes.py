import json
from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import ToolNode

from ai.agent.state import AgentState
from ai.agent.tools import TOOLS
from ai.utils.llm_utils import get_llm

llm = get_llm('TRANSCRIPT')

SYSTEM_PROMPT = """You are a helpful customer support assistant for an insurance and lending company.
You have access to the following tools:
1. `search_unstructured_interactions`: Search transcripts, chats, and emails for relevant context. Arguments: {"query": "string", "policy_id": "string (optional)"}
2. `get_database_context`: Fetch structured customer and agent details. Arguments: {"agent_id": "string (optional)"}

If you need to use a tool, you MUST output exactly a JSON block and nothing else, like this:
```json
{
  "tool": "tool_name",
  "args": {
    "arg1": "value"
  }
}
```
If you have enough information to answer the user's query, output your final answer as plain text (do NOT wrap it in JSON).
Always use the tools if you need to fetch policy details or agent information.
CRITICAL: If a tool returns "No relevant context found" or an error, DO NOT call the exact same tool with the exact same arguments again. If you cannot find the information after trying, output a final plain text answer apologizing that the information could not be found.
"""

def agent_node(state: AgentState):
    messages = state.get("messages", [])
    
    # Format messages into a single prompt string since get_llm returns a RunnableLambda 
    # and _extract_prompt_str in llm_utils expects strings or simple prompt objects.
    conversation_history = SYSTEM_PROMPT + "\n\nConversation History:\n"
    for msg in messages:
        if isinstance(msg, HumanMessage):
            conversation_history += f"User: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                conversation_history += f"Assistant (Tool Call): {msg.tool_calls[0]['name']} with args {msg.tool_calls[0]['args']}\n"
            else:
                conversation_history += f"Assistant: {msg.content}\n"
        elif isinstance(msg, ToolMessage) or msg.type == 'tool':
            conversation_history += f"Tool Output: {msg.content}\n"
            
    response_str = llm.invoke(conversation_history)
    print(f"=== LLM RAW RESPONSE ===\n{response_str}\n========================")
    
    # Check if the LLM decided to call a tool via JSON block
    if "```json" in response_str:
        try:
            json_str = response_str.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(json_str)
            tool_name = parsed.get("tool")
            args = parsed.get("args", {})
            
            # Create a manual ToolCall so LangGraph's ToolNode can process it natively
            tool_call = {
                "name": tool_name,
                "args": args,
                "id": "call_" + str(hash(response_str))[-8:].replace("-", "")
            }
            return {"messages": [AIMessage(content="", tool_calls=[tool_call])]}
        except Exception as e:
            # If JSON parsing fails, we pass the error back as a pseudo-tool response to force the LLM to fix it
            return {"messages": [AIMessage(content=f"Error parsing JSON tool call: {e}. Please ensure you output strictly valid JSON inside markdown blocks if calling a tool.")]}
            
    # If no tool call, it's the final answer
    return {"messages": [AIMessage(content=response_str.strip())]}

# The ToolNode automatically executes the tools requested via AIMessage.tool_calls
tool_node = ToolNode(TOOLS)

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Determine whether to continue to tools or end the graph."""
    messages = state.get("messages", [])
    last_message = messages[-1]
    
    if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return "__end__"
