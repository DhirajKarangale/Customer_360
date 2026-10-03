from langgraph.graph import StateGraph, END
from ai.agent.state import AgentState
from ai.agent.nodes import agent_node, tool_node, should_continue, format_text_node
from ai.agent.restrictions import restriction_node
from langchain_core.messages import AIMessage
from typing import Literal


def route_after_restriction(state: AgentState) -> Literal["agent", "__end__"]:
    messages = state.get("messages", [])
    if not messages:
        return "agent"

    last_message = messages[-1]
    if isinstance(last_message, AIMessage):
        return "__end__"

    return "agent"


def build_graph():

    workflow = StateGraph(AgentState)

    workflow.add_node("restriction", restriction_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("format_text", format_text_node)

    workflow.set_entry_point("restriction")

    workflow.add_conditional_edges(
        "restriction",
        route_after_restriction,
    )

    workflow.add_conditional_edges(
        "agent",
        should_continue,
    )

    workflow.add_edge("format_text", END)

    workflow.add_edge("tools", "agent")

    app = workflow.compile()

    return app


agent_app = build_graph()
