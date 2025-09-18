# LangGraph Workflow System

A modular and extensible workflow system built with LangGraph, featuring a router agent and multiple workflow support.

## Features

- **Router Agent**: Intelligently routes requests to the appropriate workflow
- **Modular Design**: Easily add new workflows without modifying existing code
- **State Management**: Built-in state management for tracking conversation context
- **Extensible**: Simple API for adding new nodes and workflows
- **Auto-Discovery**: Drop a domain workflow and it is auto-registered via the registry

## Project Structure

```
langgrapg/
├── core/
│   ├── __init__.py
│   ├── agent.py             # Base agent and router implementation
│   └── workflow.py          # Workflow management and builder
├── workflows/
│   ├── __init__.py
│   ├── example_workflow.py  # Example workflow (simple echo)
│   ├── registry.py          # Auto-discovery of domain workflows
│   ├── common/              # Shared nodes/utilities used by many workflows
│   │   ├── __init__.py
│   │   └── nodes.py         # Reusable nodes (banner, ensure context, finalize)
│   └── domains/             # Scalable, domain-based workflows
│       ├── __init__.py
│       ├── qa/
│       │   ├── __init__.py
│       │   └── workflow.py  # WORKFLOW_NAME = "qa"
│       ├── jdk_upgrade/
│       │   └── workflow.py  # WORKFLOW_NAME = "jdk_upgrade"
│       └── xapi_generation/
│           └── workflow.py  # WORKFLOW_NAME = "xapi_generation"
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── app.py                   # Main application entry point
```

## Getting Started

1. Create and activate a virtual environment, then install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. Run the application:
   ```bash
   python app.py
   ```

## Using the Router

The app supports simple prefix-based routing. Start your input with a prefix to route to a workflow directly:

- `qa <your question>` routes to the `qa` workflow
- `jdk <instruction>` or `jdk_upgrade ...` routes to `jdk_upgrade`
- `xapi <instruction>` or `xapi_generation ...` routes to `xapi_generation`

If no prefix is detected, the router falls back to the default workflow (`example`). You can also force a route by setting `state.context["route"]` to a workflow name in custom integrations.

## Adding a New Domain Workflow

1. Create a new directory under `workflows/domains/`, e.g. `workflows/domains/my_domain/`.
2. Inside it, create a `workflow.py` that exposes at minimum:
   - `WORKFLOW_NAME: str`
   - `create_workflow() -> Runnable`
   - Optionally `WORKFLOW_DESCRIPTION`, `WORKFLOW_DOMAIN`

   Example skeleton:
   ```python
   # workflows/domains/my_domain/workflow.py
   from typing import Dict, Any
   from langgraph.graph import END
   from core.agent import AgentState
   from core.workflow import WorkflowBuilder

   WORKFLOW_NAME = "my_domain"
   WORKFLOW_DESCRIPTION = "My domain workflow"

   def create_workflow() -> Runnable:
       # Define your workflow nodes and edges here
       # ...
       return WorkflowBuilder.create_workflow(
           nodes=nodes,
           edges=edges,
           entry_point="start",
           end_point=END
       )
```

## License

MIT
