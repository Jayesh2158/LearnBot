# DEPENDENCIES.md

Flat list of direct project dependencies. Current state only.

## Python — `requirements.txt`

| Package | Version | Purpose |
|---|---|---|
| fastapi | 0.115.6 | REST API server |
| uvicorn | 0.34.0 | ASGI server |
| groq | 0.15.0 | Groq LLM client |
| pydantic | 2.10.4 | Request/response models |
| python-dotenv | 1.0.1 | `.env` loader |
| langchain | 0.3.14 | Agent framework |
| langchain-groq | 0.2.4 | LangChain ↔ Groq adapter |
| langchain-community | 0.3.14 | LangChain community integrations |
| langgraph | 0.2.62 | `StateGraph` orchestration |

## JavaScript — `package.json`

Runtime:

| Package | Version | Purpose |
|---|---|---|
| react | ^18.2.0 | UI framework |
| react-dom | ^18.2.0 | React DOM renderer |
| axios | ^1.7.0 | HTTP client |
| lucide-react | ^0.383.0 | Icon set |
| react-markdown | ^9.0.0 | Markdown rendering for chat responses |
| react-scripts | ^5.0.1 | CRA build/dev toolchain |

No `devDependencies` declared.

## External services

- Groq API — `GROQ_API_KEY` required at runtime
- Rosetta MCP — `https://mcp.rosetta.griddynamics.net/mcp` (configured in `.mcp.json` for Claude Code)
