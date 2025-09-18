from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass
from typing import Dict, Optional, Callable, Any

from langgraph.graph import StateGraph

from core.agent import AgentState


@dataclass(frozen=True)
class WorkflowSpec:
    name: str
    builder: Callable[[], Any]
    description: str = ""
    domain: str = ""


def discover_workflows(package: str = "workflows.domains") -> Dict[str, Any]:
    """Auto-discover workflow modules under the given package.

    Each workflow module should expose:
    - WORKFLOW_NAME: str
    - create_workflow: Callable[[], Runnable]
    - optionally WORKFLOW_DESCRIPTION, WORKFLOW_DOMAIN
    """
    discovered: Dict[str, Any] = {}

    try:
        pkg = importlib.import_module(package)
    except ModuleNotFoundError:
        return discovered

    for finder, name, ispkg in pkgutil.walk_packages(pkg.__path__, prefix=f"{package}."):
        if not name.endswith(".workflow"):
            # convention: modules named 'workflow' inside each domain subpackage
            continue
        try:
            mod = importlib.import_module(name)
        except Exception:
            continue

        wf_name = getattr(mod, "WORKFLOW_NAME", None)
        builder = getattr(mod, "create_workflow", None)
        if wf_name and callable(builder):
            spec = WorkflowSpec(
                name=wf_name,
                builder=builder,
                description=getattr(mod, "WORKFLOW_DESCRIPTION", ""),
                domain=getattr(mod, "WORKFLOW_DOMAIN", ""),
            )
            try:
                discovered[wf_name] = spec.builder()
            except Exception:
                # skip workflows that fail to build
                continue

    return discovered
