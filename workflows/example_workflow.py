from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from core.workflow import WorkflowBuilder
from core.agent import AgentState, BaseAgent
from langgraph.graph import END

# Example workflow nodes
def start_node(state: AgentState) -> Dict[str, Any]:
    """Initial node that processes the input."""
    # Add a system message to the conversation
    state.setdefault("messages", [])
    state.setdefault("context", {})
    system_message = AIMessage(
        content="Welcome to the example workflow! I'll help you with your request."
    )
    state["messages"].append(system_message)
    return {"messages": state["messages"], "context": state["context"]}

def process_node(state: AgentState) -> Dict[str, Any]:
    """Process the user's request."""
    # Get the last user message
    msgs = state.get("messages", [])
    user_message = next(
        msg for msg in reversed(msgs) 
        if isinstance(msg, HumanMessage)
    )
    
    # Simple processing - in a real app, this would be more sophisticated
    response = f"I received your message: {user_message.content}"
    
    # Add the response to the conversation
    msgs.append(AIMessage(content=response))
    
    return {"messages": msgs, "context": state.get("context", {})}

# Create the workflow
def create_example_workflow():
    # Define the workflow nodes
    nodes = {
        "start": start_node,
        "process_node": process_node,
    }
    
    # Define the edges between nodes
    edges = [
        ("start", "process_node"),
        ("process_node", END),
    ]
    
    # Build and return the workflow
    return WorkflowBuilder.create_workflow(
        nodes=nodes,
        edges=edges,
        entry_point="start",
    )
