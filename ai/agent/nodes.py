import json
import os
from typing import Literal
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import ToolNode
import logging

logger = logging.getLogger(__name__)

from ai.agent.state import AgentState
from ai.agent.tools import TOOLS
from ai.utils.llm_utils import get_llm
from ai.utils.message_manager import get_message
from ai.agent.prompts import SYSTEM_PROMPT, FORMATTING_PROMPT
from ai.agent.context import resolve_names_from_state

agent_llm = get_llm("TRANSCRIPT")

format_llm = get_llm("FORMAT")


def agent_node(state: AgentState):
    import ai.agent.state

    messages = state.get("messages", [])

    ai.agent.state.CURRENT_AGENT_ID = None

    context_str, has_context = resolve_names_from_state(state)

    system_prompt_with_context = SYSTEM_PROMPT
    if has_context:
        system_prompt_with_context += context_str

    conversation_history = system_prompt_with_context + "\n\nConversation History:\n"

    tool_call_count = 0
    seen_tool_calls: set = set()

    for msg in messages:
        if isinstance(msg, HumanMessage):
            conversation_history += f"User: {msg.content}\n"
        elif isinstance(msg, AIMessage):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                tc = msg.tool_calls[0]
                tool_call_count += 1
                seen_tool_calls.add(
                    (tc["name"], frozenset(str(v) for v in tc["args"].items()))
                )
                conversation_history += (
                    f"Assistant (Tool Call): {tc['name']} with args {tc['args']}\n"
                )
            else:
                conversation_history += f"Assistant: {msg.content}\n"
        elif isinstance(msg, ToolMessage) or msg.type == "tool":
            conversation_history += f"Tool Output: {msg.content}\n"

    MAX_TOOL_CALLS = 6
    if tool_call_count >= MAX_TOOL_CALLS:
        conversation_history += (
            f"\n[SYSTEM] You have made {tool_call_count} tool calls. "
            "You MUST now output a final plain-text answer immediately. No more tool calls allowed.\n"
        )

    response_str = agent_llm.invoke(conversation_history)
    logger.info(f"=== LLM RAW RESPONSE ===\n{response_str}\n========================")

    if not response_str:
        return {
            "messages": [
                AIMessage(
                    content=get_message("general_error", "I'm sorry, I encountered an issue generating a response. Please try again.")
                )
            ]
        }

    response_str = str(response_str).strip()

    if "```json" in response_str and tool_call_count < MAX_TOOL_CALLS:
        try:
            json_str = response_str.split("```json")[1].split("```")[0].strip()
            parsed = json.loads(json_str)
            tool_name = parsed.get("tool")
            args = parsed.get("args", {})

            VALID_TOOL_ARGS = {
                "search_unstructured_interactions": {
                    "query",
                    "policy_id",
                    "customer_id",
                    "agent_id",
                },
                "get_database_context": {"agent_id", "policy_id", "customer_id"},
                "execute_sql_query": {"query"},
            }
            valid_keys = VALID_TOOL_ARGS.get(tool_name, set())
            invalid_keys = set(args.keys()) - valid_keys
            if invalid_keys:

                FIELD_REMAPS = {
                    "name": "customer_id",
                    "customer_name": "customer_id",
                    "agent_name": "agent_id",
                    "policy_number": "policy_id",
                }
                for bad_key in list(invalid_keys):
                    good_key = FIELD_REMAPS.get(bad_key)
                    if good_key and good_key in valid_keys and good_key not in args:
                        args[good_key] = args.pop(bad_key)
                    else:
                        args.pop(bad_key, None)

            call_sig = (tool_name, frozenset(str(v) for v in args.items()))
            if call_sig in seen_tool_calls:
                correction = (
                    f"[SYSTEM] You already called '{tool_name}' with these exact arguments and "
                    "received a result. Do NOT repeat this call. "
                    "You MUST now write your final plain-text answer using the information already retrieved."
                )

                forced_history = (
                    conversation_history + f"Assistant: {correction}\nAssistant:"
                )
                forced_response = agent_llm.invoke(forced_history)
                forced_response = (
                    str(forced_response).strip() if forced_response else ""
                )

                if "```json" in forced_response:
                    forced_response = forced_response.split("```json")[0].strip()
                if not forced_response:
                    forced_response = get_message("retrieval_failed", "I'm sorry, I wasn't able to retrieve the requested information. Please try rephrasing your question.")
                return {"messages": [AIMessage(content=forced_response)]}

            tool_call = {
                "name": tool_name,
                "args": args,
                "id": "call_" + str(abs(hash(response_str)))[-8:],
            }
            return {"messages": [AIMessage(content="", tool_calls=[tool_call])]}
        except Exception as e:

            return {
                "messages": [
                    AIMessage(
                        content=get_message("json_parse_error", f"Error parsing JSON tool call: {e}. Please ensure you output strictly valid JSON inside markdown blocks if calling a tool.", e=e)
                    )
                ]
            }

    return {"messages": [AIMessage(content=response_str)]}


tool_node = ToolNode(TOOLS)


def should_continue(state: AgentState) -> Literal["tools", "format_text"]:
    """Determine whether to continue to tools or end the graph."""
    messages = state.get("messages", [])
    last_message = messages[-1]

    if (
        isinstance(last_message, AIMessage)
        and hasattr(last_message, "tool_calls")
        and last_message.tool_calls
    ):
        return "tools"
    return "format_text"



def format_text_node(state: AgentState):
    messages = state.get("messages", [])
    if not messages:
        return {"messages": []}

    last_message = messages[-1]

    if (
        os.getenv("ENABLE_TEXT_FORMAT") == "True"
        and isinstance(last_message, AIMessage)
        and last_message.content
    ):
        content_str = last_message.content.strip()

        _SKIP_PREFIXES = (
            "[SYSTEM]",
            "Error",
            "Error:",
            "SYSTEM ERROR",
            "ACCESS DENIED",
            "I'm sorry",
        )
        if any(content_str.startswith(p) for p in _SKIP_PREFIXES):
            return {"messages": []}

        prompt = FORMATTING_PROMPT.format(text=content_str)
        formatted_content = format_llm.invoke(prompt)

        if not formatted_content:

            return {"messages": []}

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
