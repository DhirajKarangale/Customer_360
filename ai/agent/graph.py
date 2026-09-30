from langgraph.graph import StateGraph, END
from ai.agent.state import AgentState
from ai.agent.nodes import agent_node, tool_node, should_continue

def build_graph():
    # Initialize the StateGraph with our AgentState
    workflow = StateGraph(AgentState)
    
    # Add the nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    
    # Define the edges
    workflow.set_entry_point("agent")
    
    # Conditional edge from agent to determine if we need tools or if we're done
    workflow.add_conditional_edges(
        "agent",
        should_continue,
    )
    
    # Normal edge from tools back to agent
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    app = workflow.compile()
    
    return app

agent_app = build_graph()
