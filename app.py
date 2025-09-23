import os
from dotenv import load_dotenv
from core.agent import AgentState, RouterAgent
from core.workflow import WorkflowManager
from workflows.example_workflow import create_example_workflow
from workflows.registry import discover_workflows
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

def initialize_workflows() -> WorkflowManager:
    """Initialize and register all workflows."""
    workflow_manager = WorkflowManager()
    
    # Register the example workflow
    example_workflow = create_example_workflow()
    workflow_manager.register_workflow("example", example_workflow, is_default=True)
    
    # Auto-discover domain workflows
    discovered = discover_workflows()
    for name, wf in discovered.items():
        # Do not override default if already set
        workflow_manager.register_workflow(name, wf, is_default=False)
    
    return workflow_manager

def main():
    # Initialize workflows
    workflow_manager = initialize_workflows()
    
    # Prepare workflows dict for router
    workflows = workflow_manager.workflows

    # Simple rule-based routing function
    def route_func(state: AgentState, workflows_dict):
        text = ""
        for msg in reversed(state.messages):
            if isinstance(msg, HumanMessage):
                text = msg.content or ""
                break
        # Simple heuristics: prefix based routing
        lower = text.lower()
        if lower.startswith("qa ") or lower.startswith("qa:"):
            return "qa" if "qa" in workflows_dict else None
        if lower.startswith("jdk ") or lower.startswith("jdk:") or lower.startswith("jdk_upgrade"):
            return "jdk_upgrade" if "jdk_upgrade" in workflows_dict else None
        if lower.startswith("xapi ") or lower.startswith("xapi:") or lower.startswith("xapi_generation"):
            return "xapi_generation" if "xapi_generation" in workflows_dict else None
        return None  # fall back to default

    # Initialize the router agent
    router = RouterAgent(workflows=workflows, route_func=route_func)
    
    print("Welcome to the LangGraph Workflow System!")
    print("Type 'exit' to quit.")
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        # Create initial state (TypedDict / dict)
        state: AgentState = {
            "messages": [HumanMessage(content=user_input)],
            "context": {"user_id": "demo_user"},
        }
        
        try:
            # Route to the appropriate workflow
            state = router.process(state)

            # Run the workflow
            result = workflow_manager.run_workflow(state, state.get("next"))

            # Display the response
            msgs = result.get("messages", []) if isinstance(result, dict) else []
            last_ai = next((m for m in reversed(msgs) if isinstance(m, AIMessage)), None)
            if last_ai:
                print(f"\nAssistant: {last_ai.content}")
            else:
                print("\nAssistant: [No AI response produced]")
            
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
