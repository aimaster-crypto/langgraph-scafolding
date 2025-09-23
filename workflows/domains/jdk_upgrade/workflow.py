from typing import Dict, Any

from langgraph.graph import END
from langchain_core.messages import AIMessage, HumanMessage

from core.agent import AgentState
from core.workflow import WorkflowBuilder
from workflows.common.nodes import start_with_banner, ensure_issue_context, finalize_with_summary

WORKFLOW_NAME = "jdk_upgrade"
WORKFLOW_DESCRIPTION = "Assists with planning and summarizing a JDK version upgrade task."
WORKFLOW_DOMAIN = "devops"


def assess_project(state: AgentState) -> Dict[str, Any]:
    # In real life, inspect repo/tooling. Here, just respond.
    state.setdefault("messages", [])
    state["messages"].append(
        AIMessage(content="(jdk) Checking current JDK version, build files, and dependencies...")
    )
    return {"messages": state["messages"]}


def suggest_steps(state: AgentState) -> Dict[str, Any]:
    steps = (
        "(jdk) Suggested steps: 1) Update toolchain, 2) Adjust compiler level, "
        "3) Update deps, 4) Run tests, 5) Fix breaking changes."
    )
    state.setdefault("messages", [])
    state["messages"].append(AIMessage(content=steps))
    return {"messages": state["messages"]}


def create_workflow():
    nodes = {
        "start": lambda s: start_with_banner(s, "Starting JDK upgrade workflow."),
        "context": ensure_issue_context,
        "assess": assess_project,
        "plan": suggest_steps,
        "finalize": lambda s: finalize_with_summary(s, prefix="JDK Upgrade Summary"),
    }
    edges = [
        ("start", "context"),
        ("context", "assess"),
        ("assess", "plan"),
        ("plan", "finalize"),
        ("finalize", END),
    ]
    return WorkflowBuilder.create_workflow(nodes=nodes, edges=edges, entry_point="start")
