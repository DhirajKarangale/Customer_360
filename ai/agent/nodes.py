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
1. `search_unstructured_interactions`: Search transcripts, chats, and emails for relevant context. Arguments: {"query": "string", "policy_id": "string (optional)", "customer_id": "string (optional)", "agent_id": "string (optional)"}
2. `get_database_context`: Fetch structured customer, agent, or policy details from the database. Arguments: {"agent_id": "string (optional)", "policy_id": "string (optional)", "customer_id": "string (optional)"}
3. `execute_sql_query`: Execute a raw PostgreSQL query to answer complex or aggregated questions. Tables available: customers, insurance_agents, policies, customer_interactions. Arguments: {"query": "string"}

When the user uses pronouns like "I", "me", "my", or "my policies", they are referring to the Logged-In Agent specified in the [Current Session Context], and you should filter queries to their agent ID.
If the user asks about a specific person's name, FIRST check if their name exactly matches the 'Logged-in Agent Name' or 'Active Customer Name' in the [Current Session Context]. If it matches, use the ID provided in the context directly! Do not look them up.
IMPORTANT SQL RULE: Text fields in PostgreSQL (like 'status') are case-sensitive. When filtering by text in SQL (e.g. status='active'), you MUST use ILIKE instead of = (e.g. status ILIKE 'active') to ensure it matches 'Active', 'Pending', etc.
If the name is NOT in the context, you must determine if that person is a customer or another insurance agent by checking both the `customers` and `insurance_agents` tables using the `get_database_context` tool. Do NOT blindly apply the Logged-In Agent ID filter if the person is another agent.

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
When summarizing unstructured interactions (like emails or chats), ALWAYS include specific names, examples, or details from the retrieved context to make the answer as concrete as possible.
CRITICAL: If a tool returns "No relevant context found" or an error, DO NOT call the exact same tool with the exact same arguments again. If you cannot find the information after trying, output a final plain text answer apologizing that the information could not be found.
"""


def agent_node(state: AgentState):
    import ai.agent.state
    messages = state.get("messages", [])
    
    # Inject contextual IDs if they exist
    context_str = "\n[Current Session Context]\n"
    has_context = False
    
    # Reset it by default
    ai.agent.state.CURRENT_AGENT_ID = None
    
    from ai.agent.restrictions import restriction_manager
    if state.get("insurance_agents_id"):
        agent_uuid = state['insurance_agents_id']
        
        # Resolve agent name to make the context more human-readable for the LLM
        agent_name = "Unknown Agent"
        from ai.agent.tools import AIDatabaseAccess
        db = AIDatabaseAccess()
        try:
            res = db.execute_query(f"SELECT name FROM insurance_agents WHERE id = '{agent_uuid}'")
            lines = [line.strip() for line in res.split('\n') if line.strip() and not line.startswith('-')]
            if len(lines) > 1 and lines[0].lower() == 'name':
                agent_name = lines[1]
        except Exception:
            pass
        finally:
            db.close()
            
        context_str += f"- Logged-in Agent ID: {agent_uuid}\n"
        context_str += f"- Logged-in Agent Name: {agent_name}\n"
        has_context = True
        ai.agent.state.CURRENT_AGENT_ID = agent_uuid
    if state.get("customers_id"):
        cust_uuid = state['customers_id']
        cust_name = "Unknown Customer"
        from ai.agent.tools import AIDatabaseAccess
        db = AIDatabaseAccess()
        try:
            res = db.execute_query(f"SELECT name FROM customers WHERE id = '{cust_uuid}'")
            lines = [line.strip() for line in res.split('\n') if line.strip() and not line.startswith('-')]
            if len(lines) > 1 and lines[0].lower() == 'name':
                cust_name = lines[1]
        except Exception:
            pass
        finally:
            db.close()
        context_str += f"- Active Customer ID: {cust_uuid}\n"
        context_str += f"- Active Customer Name: {cust_name}\n"
        has_context = True
        
    if state.get("policies_id"):
        pol_uuid = state['policies_id']
        pol_number = "Unknown Policy"
        from ai.agent.tools import AIDatabaseAccess
        db = AIDatabaseAccess()
        try:
            res = db.execute_query(f"SELECT policy_number FROM policies WHERE id = '{pol_uuid}'")
            lines = [line.strip() for line in res.split('\n') if line.strip() and not line.startswith('-')]
            if len(lines) > 1 and lines[0].lower() == 'policy_number':
                pol_number = lines[1]
        except Exception:
            pass
        finally:
            db.close()
        context_str += f"- Active Policy ID: {pol_uuid}\n"
        context_str += f"- Active Policy Number: {pol_number}\n"
        has_context = True
        
    system_prompt_with_context = SYSTEM_PROMPT
    if has_context:
        system_prompt_with_context += context_str
        
    conversation_history = system_prompt_with_context + "\n\nConversation History:\n"
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
