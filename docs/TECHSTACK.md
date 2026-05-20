# TECHSTACK.md

This file lists the tech stack of all modules. Current state only — no change log.

## Backend — Python

- Language: Python 3.11+
- Web framework: FastAPI (`fastapi==0.115.6`) — REST endpoints in [main.py](../main.py)
- ASGI server: Uvicorn (`uvicorn==0.34.0`) — `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
- LLM orchestration: LangGraph (`langgraph==0.2.62`) — single-turn `StateGraph` in [graph.py](../graph.py)
- LLM agent layer: LangChain + LangChain-Community (`langchain==0.3.14`, `langchain-community==0.3.14`) — `create_tool_calling_agent` + `AgentExecutor` in [tools_agents.py](../tools_agents.py)
- LLM provider: Groq via LangChain integration (`langchain-groq==0.2.4`, `groq==0.15.0`); default model `llama-3.3-70b-versatile` (the previous `llama-3.1-70b-versatile` was decommissioned by Groq on 2026-05-19)
- Validation: Pydantic v2 (`pydantic==2.10.4`) — request/response models in [main.py](../main.py)
- Env loading: `python-dotenv==1.0.1` reads `.env` in [config.py](../config.py)

## Frontend — JavaScript / React

- Language: JavaScript (no TypeScript)
- UI framework: React 18 (`react@^18.2.0`, `react-dom@^18.2.0`)
- Build tool: Create React App (`react-scripts@^5.0.1`) — `npm start` runs dev server on :3000 with proxy to :8000
- HTTP client: Axios (`axios@^1.7.0`)
- Icons: `lucide-react@^0.383.0`
- Markdown rendering: `react-markdown@^9.0.0`
- Layout: standard CRA — `public/index.html`, `src/index.js`, `src/App.js`, `src/styles/App.css`

## Tooling / Process

- Test runner: none configured (no `pytest`, no `npm test`). "Test matrix" is a static data structure exposed via `GET /api/test-matrix` ([guardrails.py:TEST_MATRIX](../guardrails.py))
- Package managers: pip (`requirements.txt`), npm (`package.json` + `package-lock.json`)
- Coding agent: Claude Code + Rosetta MCP (`.mcp.json` points at `https://mcp.rosetta.griddynamics.net/mcp`)
- Source control: git

## Key stack decisions

- **TypedDict for `LearnBotState`** (not plain dict) — typo protection + LangGraph reducer semantics ([graph.py](../graph.py)).
- **Conditional edges, not a router node** — branching is declarative in the graph topology so it stays introspectable.
- **Stateless per-request** — no checkpointer; conversation history does not persist across `/api/chat` calls despite `messages` being append-only within one run.
- **Scoped agent tool-sets** — `create_tool_calling_agent` restricts each of the three agents (course, support, faq) to a subset of `@tool`-decorated functions. The scoping is the security boundary.
- **Regex-only guardrails** — `education_injection_detector` uses pure functions across 5 categories with CRITICAL severity short-circuiting the graph; no LLM call in the guardrail.
- **Flat repo layout** — README mentions `backend/` and `frontend/` directories but the actual layout is a single flat project at root.
