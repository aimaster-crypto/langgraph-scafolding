from typing import Dict, Any

from langgraph.graph import END
from langchain_core.messages import AIMessage, HumanMessage

from core.agent import AgentState
from core.workflow import WorkflowBuilder
from workflows.common.nodes import start_with_banner, ensure_issue_context, finalize_with_summary

WORKFLOW_NAME = "xapi_generation"
WORKFLOW_DESCRIPTION = "Generates or scaffolds an xAPI statement schema or sample payloads from instructions."
WORKFLOW_DOMAIN = "content"


def parse_requirements(state: AgentState) -> Dict[str, Any]:
    msgs = state.get("messages", [])
    last_user = next((m for m in reversed(msgs) if isinstance(m, HumanMessage)), None)
    brief = last_user.content if last_user else "No requirements provided."
    ctx = state.get("context", {})
    ctx["xapi_requirements"] = brief
    msgs.append(AIMessage(content=f"(xapi) Parsed requirements: {brief}"))
    return {"messages": msgs, "context": ctx}


def propose_schema(state: AgentState) -> Dict[str, Any]:
    ctx = state.get("context", {})
    msgs = state.get("messages", [])
    req = ctx.get("xapi_requirements", "")
    msgs.append(
        AIMessage(
            content=(
                "(xapi) Proposed statement template: {\n"
                "  'actor': {...}, 'verb': 'experienced', 'object': {...},\n"
                "  'context': {...}, 'result': {...}\n} based on: " + req
            )
        )
    )
    return {"messages": msgs, "context": ctx}


def create_workflow():
    nodes = {
        "start": lambda s: start_with_banner(s, "Starting xAPI generation workflow."),
        "context": ensure_issue_context,
        "parse": parse_requirements,
        "schema": propose_schema,
        "finalize": lambda s: finalize_with_summary(s, prefix="xAPI Generation Summary"),
    }
    edges = [
        ("start", "context"),
        ("context", "parse"),
        ("parse", "schema"),
        ("schema", "finalize"),
        ("finalize", END),
    ]
    return WorkflowBuilder.create_workflow(nodes=nodes, edges=edges, entry_point="start")
