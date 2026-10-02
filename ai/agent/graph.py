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
    
    # If the restriction node appended an AIMessage, it means access was denied
    last_message = messages[-1]
    if isinstance(last_message, AIMessage):
        return "__end__"
        
    return "agent"

def build_graph():
    # Initialize the StateGraph with our AgentState
    workflow = StateGraph(AgentState)
    
    # Add the nodes
    workflow.add_node("restriction", restriction_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("format_text", format_text_node)
    
    # Define the edges
    workflow.set_entry_point("restriction")
    
    workflow.add_conditional_edges(
        "restriction",
        route_after_restriction,
    )
    
    # Conditional edge from agent to determine if we need tools or if we're done
    workflow.add_conditional_edges(
        "agent",
        should_continue,
    )
    
    workflow.add_edge("format_text", END)
    
    # Normal edge from tools back to agent
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    app = workflow.compile()
    
    return app

agent_app = build_graph()
