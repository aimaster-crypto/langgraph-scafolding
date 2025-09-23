from typing import Dict, List, Optional, Type, Union, Callable, Any
from langgraph.graph import StateGraph, END
from .agent import AgentState, BaseAgent

class WorkflowManager:
    """Manages multiple workflows and their execution."""
    
    def __init__(self):
        self.workflows: Dict[str, Any] = {}
        self.default_workflow: Optional[str] = None
    
    def register_workflow(
        self, 
        name: str, 
        workflow: Any,
        is_default: bool = False
    ) -> None:
        """Register a new workflow."""
        self.workflows[name] = workflow
        if is_default or not self.default_workflow:
            self.default_workflow = name
    
    def get_workflow(self, name: Optional[str] = None) -> Any:
        """Get a workflow by name, or the default if none specified."""
        if name is None:
            if not self.default_workflow:
                raise ValueError("No default workflow set")
            name = self.default_workflow
        
        if name not in self.workflows:
            raise ValueError(f"Unknown workflow: {name}")
            
        return self.workflows[name]
    
    def run_workflow(
        self, 
        input_state: AgentState, 
        workflow_name: Optional[str] = None
    ) -> AgentState:
        """Run a workflow with the given input state."""
        workflow = self.get_workflow(workflow_name)
        return workflow.invoke(input_state)

class WorkflowBuilder:
    """Helper class to build workflows."""
    
    @staticmethod
    def create_workflow(
        nodes: Dict[str, Callable],
        edges: List[tuple],
        entry_point: str = "start",
    ) -> Any:
        """Create and compile a workflow with the given nodes and edges.

        Edges can point to other node names or the END sentinel, e.g. ("process", END).
        """
        graph = StateGraph(AgentState)

        # Add nodes
        for name, node in nodes.items():
            graph.add_node(name, node)

        # Set entry point
        graph.set_entry_point(entry_point)

        # Add edges (support END)
        for from_node, to_node in edges:
            graph.add_edge(from_node, to_node)

        # Compile
        return graph.compile()
