from typing import Dict, Any, Optional
from langchain_core.messages import AIMessage, HumanMessage
from core.agent import AgentState


def start_with_banner(state: AgentState, banner: Optional[str] = None) -> Dict[str, Any]:
    msg = banner or "Starting workflow."
    state.setdefault("messages", [])
    state.setdefault("context", {})
    state["messages"].append(AIMessage(content=msg))
    return {"messages": state["messages"], "context": state["context"]}


def ensure_issue_context(state: AgentState) -> Dict[str, Any]:
    """Ensure minimal context exists. In real use, might fetch repo, issue, etc."""
    ctx = state.get("context", {}) or {}
    ctx.setdefault("user_id", "demo_user")
    ctx.setdefault("trace_id", "local-0001")
    return {"context": ctx}


def finalize_with_summary(state: AgentState, prefix: str = "Done:") -> Dict[str, Any]:
    msgs = state.get("messages", [])
    last_user = next((m for m in reversed(msgs) if isinstance(m, HumanMessage)), None)
    summary = f"{prefix} processed request" + (f": {last_user.content}" if last_user else ".")
    msgs.append(AIMessage(content=summary))
    return {"messages": msgs, "context": state.get("context", {})}
