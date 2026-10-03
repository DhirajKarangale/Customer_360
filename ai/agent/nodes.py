import json
import os
from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import ToolNode

from ai.agent.state import AgentState
from ai.agent.tools import TOOLS
from ai.utils.llm_utils import get_llm

# Main agent LLM — handles reasoning, tool calls, and response generation
agent_llm = get_llm('TRANSCRIPT')
# Lightweight LLM for the HTML formatting pass only
format_llm = get_llm('FORMAT')

SYSTEM_PROMPT = """You are a helpful customer support assistant for an insurance and lending company.
You have access to the following tools:
1. `search_unstructured_interactions`: Search transcripts, chats, and emails for relevant context. Arguments: {"query": "string", "policy_id": "string (optional)", "customer_id": "string or name (optional)", "agent_id": "string or name (optional)"}
2. `get_database_context`: Fetch structured customer, agent, or policy details from the database. Arguments: {"agent_id": "UUID or name (optional)", "policy_id": "UUID or policy number (optional)", "customer_id": "UUID or customer name (optional)"}
3. `execute_sql_query`: Execute a raw PostgreSQL query to answer complex or aggregated questions. Arguments: {"query": "string"}

╔══ TOOL ARGUMENT RULES (CRITICAL) ════════════════════════════════════════════╗
║ `customer_id` accepts EITHER a UUID OR a customer name string               ║
║ `agent_id`   accepts EITHER a UUID OR an agent name string                  ║
║ `policy_id`  accepts EITHER a UUID OR a policy number string                ║
║ NEVER invent fields like `name`, `customer_name`, `agent_name` — they      ║
║ do NOT exist. ONLY use: customer_id, agent_id, policy_id, query.           ║
╚═════════════════════════════════════════════════════════════════════════════╝

═══ EXACT DATABASE SCHEMA (use ONLY these column names in SQL) ═══
customers:          id (uuid), name, email, phone_number, date_of_birth, address, created_at
insurance_agents:   id (uuid), name, email, phone_number, agency_name, license_number
policies:           id (uuid), policy_number, customer_id (→ customers.id), agent_id (→ insurance_agents.id),
                    policy_type, status, start_date, end_date, premium_amount, coverage_amount
customer_interactions: id (uuid), customer_id (→ customers.id), agent_id (→ insurance_agents.id),
                       policy_number, interaction_type, interaction_date
agent_chats:        job_id, agent_id, customer_id, policy_id, query, message, status, send_time
═══════════════════════════════════════════════════════════════════

RULES:
- You MUST ALWAYS filter queries on `policies`, `customers`, or `customer_interactions` by the Logged-In Agent ID in [Current Session Context], UNLESS the user explicitly asks about a different specific agent.
- If the user asks about a person's name, FIRST check if it matches 'Logged-in Agent Name' or 'Active Customer Name' in [Current Session Context]. If it matches, use that ID directly — do NOT look them up again.
- If you know a customer's name from Conversation History but don't have their UUID, pass that name as `customer_id` to `get_database_context` — the tool supports name-based lookup automatically.
- SQL text fields (like `status`) are case-insensitive in practice but use ILIKE for safety: `status ILIKE 'active'`.
- If a name is NOT in context, check both `customers` and `insurance_agents` tables using `get_database_context`.

CRITICAL ANTI-LOOP RULES (enforce strictly):
1. NEVER call the exact same tool with the exact same arguments more than once. If a tool already returned a result for given args, use that result — do NOT repeat the call.
2. If a tool returns an error or empty result, try ONE alternative approach. If that also fails, give a final plain-text answer explaining what you tried.
3. You have a maximum of 6 tool calls per response. After 6 calls, you MUST output a final plain-text answer immediately regardless of whether you have complete information.
4. NEVER invent tool arguments that are not listed above. Invalid args are silently ignored — your call will return no useful data.

If you need to use a tool, output EXACTLY a JSON block and nothing else:
```json
{
  "tool": "tool_name",
  "args": {
    "arg1": "value"
  }
}
```
If you have enough information to answer, output plain text directly. DO NOT prefix with "Assistant:".
When summarizing interactions, ALWAYS include specific names, examples, or details from the retrieved context.
"""



def _resolve_names_from_state(state: AgentState) -> tuple[str, bool]:
    """
    Opens a SINGLE DB connection to resolve agent name, customer name, and
    policy number from UUIDs in the state. Returns (context_string, has_context).
    Significantly cheaper than opening 3 separate connections.
    """
    import ai.agent.state
    from ai.agent.tools import AIDatabaseAccess

    agent_uuid = state.get("insurance_agents_id")
    cust_uuid = state.get("customers_id")
    pol_uuid = state.get("policies_id")

    if not agent_uuid and not cust_uuid and not pol_uuid:
        return "", False

    context_lines = []
    has_context = False

    db = AIDatabaseAccess()
    try:
        if agent_uuid:
            try:
                res = db.execute_query(
                    f"SELECT name FROM insurance_agents WHERE id = '{agent_uuid}'"
                )
                lines = [l.strip() for l in res.splitlines() if l.strip() and not l.startswith('-')]
                agent_name = lines[1] if len(lines) > 1 and lines[0].lower() == 'name' else "Unknown Agent"
            except Exception:
                agent_name = "Unknown Agent"
            context_lines.append(f"- Logged-in Agent ID: {agent_uuid}")
            context_lines.append(f"- Logged-in Agent Name: {agent_name}")
            has_context = True
            ai.agent.state.CURRENT_AGENT_ID = agent_uuid

        if cust_uuid:
            try:
                res = db.execute_query(
                    f"SELECT name FROM customers WHERE id = '{cust_uuid}'"
                )
                lines = [l.strip() for l in res.splitlines() if l.strip() and not l.startswith('-')]
                cust_name = lines[1] if len(lines) > 1 and lines[0].lower() == 'name' else "Unknown Customer"
            except Exception:
                cust_name = "Unknown Customer"
            context_lines.append(f"- Active Customer ID: {cust_uuid}")
            context_lines.append(f"- Active Customer Name: {cust_name}")
            has_context = True

        if pol_uuid:
            try:
                res = db.execute_query(
                    f"SELECT policy_number FROM policies WHERE id = '{pol_uuid}'"
                )
                lines = [l.strip() for l in res.splitlines() if l.strip() and not l.startswith('-')]
                pol_number = lines[1] if len(lines) > 1 and lines[0].lower() == 'policy_number' else "Unknown Policy"
            except Exception:
                pol_number = "Unknown Policy"
            context_lines.append(f"- Active Policy ID: {pol_uuid}")
            context_lines.append(f"- Active Policy Number: {pol_number}")
            has_context = True

    finally:
        db.close()

    context_str = "\n[Current Session Context]\n" + "\n".join(context_lines) if context_lines else ""
    return context_str, has_context


def agent_node(state: AgentState):
    import ai.agent.state

    messages = state.get("messages", [])

    # Reset current agent ID at the start of every node invocation
    ai.agent.state.CURRENT_AGENT_ID = None

    # Resolve all context names using a SINGLE shared DB connection
    context_str, has_context = _resolve_names_from_state(state)

    system_prompt_with_context = SYSTEM_PROMPT
    if has_context:
        system_prompt_with_context += context_str

    conversation_history = system_prompt_with_context + "\n\nConversation History:\n"

    # Count how many tool calls have already been made in this conversation turn,
    # and collect (tool, args) pairs to detect duplicate calls.
    tool_call_count = 0
    seen_tool_calls: set = set()  # frozenset of (tool_name, sorted_args_items)

    for msg in messages:
        if isinstance(msg, HumanMessage):
            conversation_history += f"User: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tc = msg.tool_calls[0]
                tool_call_count += 1
                seen_tool_calls.add((tc['name'], frozenset(str(v) for v in tc['args'].items())))
                conversation_history += f"Assistant (Tool Call): {tc['name']} with args {tc['args']}\n"
            else:
                conversation_history += f"Assistant: {msg.content}\n"
        elif isinstance(msg, ToolMessage) or msg.type == 'tool':
            conversation_history += f"Tool Output: {msg.content}\n"

    # Hard cap: force a final answer if the agent has already made MAX_TOOL_CALLS
    MAX_TOOL_CALLS = 6
    if tool_call_count >= MAX_TOOL_CALLS:
        conversation_history += (
            f"\n[SYSTEM] You have made {tool_call_count} tool calls. "
            "You MUST now output a final plain-text answer immediately. No more tool calls allowed.\n"
        )

    response_str = agent_llm.invoke(conversation_history)
    print(f"=== LLM RAW RESPONSE ===\n{response_str}\n========================")

    # Guard: if Snowflake returns None for some reason, return a safe fallback
    if not response_str:
        return {"messages": [AIMessage(content="I'm sorry, I encountered an issue generating a response. Please try again.")]}

    response_str = str(response_str).strip()

    # Check if the LLM decided to call a tool via JSON block
    if "```json" in response_str and tool_call_count < MAX_TOOL_CALLS:
        try:
            json_str = response_str.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(json_str)
            tool_name = parsed.get("tool")
            args = parsed.get("args", {})

            # Strip out any invalid/invented fields the LLM may hallucinate.
            # Only keep args that are actually accepted by our tools.
            VALID_TOOL_ARGS = {
                "search_unstructured_interactions": {"query", "policy_id", "customer_id", "agent_id"},
                "get_database_context":             {"agent_id", "policy_id", "customer_id"},
                "execute_sql_query":                {"query"},
            }
            valid_keys = VALID_TOOL_ARGS.get(tool_name, set())
            invalid_keys = set(args.keys()) - valid_keys
            if invalid_keys:
                # Remap common hallucinations to the correct field
                FIELD_REMAPS = {
                    "name": "customer_id", "customer_name": "customer_id",
                    "agent_name": "agent_id", "policy_number": "policy_id",
                }
                for bad_key in list(invalid_keys):
                    good_key = FIELD_REMAPS.get(bad_key)
                    if good_key and good_key in valid_keys and good_key not in args:
                        args[good_key] = args.pop(bad_key)
                    else:
                        args.pop(bad_key, None)

            # Deduplication: if this exact (tool, args) combo was already called,
            # inject a strong correction and force a final plain-text answer.
            call_sig = (tool_name, frozenset(str(v) for v in args.items()))
            if call_sig in seen_tool_calls:
                correction = (
                    f"[SYSTEM] You already called '{tool_name}' with these exact arguments and "
                    "received a result. Do NOT repeat this call. "
                    "You MUST now write your final plain-text answer using the information already retrieved."
                )
                # Append the correction and re-invoke the LLM immediately so it
                # produces a real answer instead of leaking the system message.
                forced_history = conversation_history + f"Assistant: {correction}\nAssistant:"
                forced_response = agent_llm.invoke(forced_history)
                forced_response = str(forced_response).strip() if forced_response else ""
                # If LLM still tries a tool call, strip it and use whatever text we got
                if "```json" in forced_response:
                    forced_response = forced_response.split("```json")[0].strip()
                if not forced_response:
                    forced_response = "I'm sorry, I wasn't able to retrieve the requested information. Please try rephrasing your question."
                return {"messages": [AIMessage(content=forced_response)]}

            # Create a manual ToolCall so LangGraph's ToolNode can process it natively
            tool_call = {
                "name": tool_name,
                "args": args,
                "id": "call_" + str(abs(hash(response_str)))[-8:]
            }
            return {"messages": [AIMessage(content="", tool_calls=[tool_call])]}
        except Exception as e:
            # If JSON parsing fails, feed the error back so the LLM can correct itself
            return {"messages": [AIMessage(content=f"Error parsing JSON tool call: {e}. Please ensure you output strictly valid JSON inside markdown blocks if calling a tool.")]}

    # If no tool call, it's the final answer
    return {"messages": [AIMessage(content=response_str)]}


# The ToolNode automatically executes the tools requested via AIMessage.tool_calls
tool_node = ToolNode(TOOLS)


def should_continue(state: AgentState) -> Literal["tools", "format_text"]:
    """Determine whether to continue to tools or end the graph."""
    messages = state.get("messages", [])
    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return "format_text"


FORMATTING_PROMPT = """You are a text formatter. Convert the following text into clean semantic HTML.
Do NOT change, add, or remove any content, facts, or data. Only add HTML structure.

RULES:
1. If the text is a short simple sentence (1-2 lines), wrap it in a single <p> tag.
2. If the text has a clear title/heading followed by body content, use <h3> for the title and <p> for each paragraph.
3. If the text contains numbered items or bullet points, use <h3> for the title and <ul><li> for each point.
4. If the text has multiple sections (each with a sub-heading), use <h3> for each sub-heading, <p> for paragraphs, <ul><li> for lists.
5. For key terms, names, policy numbers, or important values, wrap them in <strong>.
6. Use <br> only to separate paragraphs if needed.

DO NOT:
- Add any CSS classes, styles, or attributes
- Add any div tags
- Add any Tailwind classes
- Use inline styles
- Wrap output in ```html blocks
- Add any content not in the original text

Just output raw HTML tags: <p>, <h3>, <ul>, <li>, <strong>, <br>. Nothing else.

Text to format:
{text}
"""


def format_text_node(state: AgentState):
    messages = state.get("messages", [])
    if not messages:
        return {"messages": []}

    last_message = messages[-1]

    if os.getenv("ENABLE_TEXT_FORMAT") == "True" and isinstance(last_message, AIMessage) and last_message.content:
        content_str = last_message.content.strip()

        # Skip formatting for system/error messages — never send internal
        # control messages to the frontend as formatted HTML.
        _SKIP_PREFIXES = ("[SYSTEM]", "Error", "Error:", "SYSTEM ERROR", "ACCESS DENIED", "I'm sorry")
        if any(content_str.startswith(p) for p in _SKIP_PREFIXES):
            return {"messages": []}

        prompt = FORMATTING_PROMPT.format(text=content_str)
        formatted_content = format_llm.invoke(prompt)

        if not formatted_content:
            # If formatting fails, just pass through the unformatted message
            return {"messages": []}

        # Strip markdown code fences if the LLM wraps them
        content = str(formatted_content).strip()
        if content.startswith("```html"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        return {"messages": [AIMessage(content=content)]}

    return {"messages": []}
