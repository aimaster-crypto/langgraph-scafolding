from typing import Any, Dict, List, Optional, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AgentState(TypedDict, total=False):
    """State that flows through the agent workflow.

    This is a TypedDict to stay lightweight and compatible with LangGraph.
    """
    messages: List[BaseMessage]
    context: Dict[str, Any]
    next: Optional[str]

class BaseAgent:
    """Base class for all agents."""
    
    def __init__(self, model_name: str = "gpt-4-0125-preview", temperature: float = 0.0):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def process(self, state: AgentState, config: Optional[RunnableConfig] = None) -> AgentState:
        """Process the input state and return the updated state."""
        raise NotImplementedError("Subclasses must implement this method")

class RouterAgent(BaseAgent):
    """Agent that routes between different workflows based on input."""
    
    def __init__(self, workflows: Dict[str, Runnable], route_func: Optional[Any] = None, **kwargs):
        super().__init__(**kwargs)
        self.workflows = workflows
        self.route_func = route_func
    
    def process(self, state: AgentState, config: Optional[RunnableConfig] = None) -> AgentState:
        """Determine which workflow to use based on the input."""
        # Ensure expected keys exist
        state.setdefault("context", {})
        state.setdefault("messages", [])

        # 1) Explicit override via state["context"]
        explicit = state["context"].get("route")
        if explicit and explicit in self.workflows:
            state["next"] = explicit
            return state

        # 2) Custom route function if provided
        if self.route_func is not None:
            try:
                chosen = self.route_func(state, self.workflows)
                if chosen in self.workflows:
                    state["next"] = chosen
                    return state
            except Exception:
                pass

        # 3) Fallback to first workflow
        state["next"] = next(iter(self.workflows.keys()))
        return state
