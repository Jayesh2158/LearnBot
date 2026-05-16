# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo layout vs. README

The README describes a `backend/` and `frontend/` split, but the actual layout is a **single flat project at the repo root**:

- Python backend modules: `config.py`, `prompts.py`, `guardrails.py`, `tools_agents.py`, `graph.py`, `main.py` — at root
- React frontend: `package.json` at root, `public/index.html`, `src/index.js`, `src/App.js`, `src/App.css` (standard CRA layout)
- Python deps: `requirements.txt` (at root); env template: `.env.example` → `.env` at root

When the README says `cd backend` or `cd frontend`, that does not match this repo — run all commands from the repo root.

## Commands

Backend (Python 3.11+, all Python files at root):

```bash
pip install -r requirements.txt
cp .env.example .env            # then fill in GROQ_API_KEY, TAVILY_API_KEY
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# Swagger UI: http://localhost:8000/docs
```

Frontend (React 18, standard CRA layout `public/` + `src/`):

```bash
npm install
npm start                       # CRA dev server on :3000, proxies to :8000
npm run build
```

If `npm start` fails with `sh: react-scripts: command not found`, delete `node_modules/` and `package-lock.json`, then reinstall — a prior broken lockfile pinned `react-scripts` to a `0.0.0` stub.

There is no test runner configured (no `pytest`, no `npm test` script). The "test matrix" is data exposed via `GET /api/test-matrix`, not an executable test suite.

## Architecture (the big picture)

Single-turn, stateless request pipeline. Each `/api/chat` call runs a fresh LangGraph traversal — no checkpointer is wired up, so conversation history does not persist across requests despite `LearnBotState.messages` being append-only within one run.

Request flow:

```
FastAPI (main.py)
  └─ run_learnbot(message)  →  LangGraph StateGraph (graph.py)
       receive_input
         └─ safety_check                       (guardrails.education_injection_detector)
              ├─ unsafe  → rejection_handler → END
              └─ safe    → intent_classifier
                              ├─ course   → course_handler   (tools_agents.get_course_agent)
                              ├─ support  → support_handler  (tools_agents.get_support_agent)
                              └─ faq      → faq_handler      (tools_agents.get_faq_agent)
                                              └─ → END
```

Layering — keep these boundaries when editing:

- **`prompts.py`** (Part A) — three `ChatPromptTemplate`s, each pre-bound with `.partial(platform_name=..., current_date=...)`. Only dynamic vars (`{query}`, `{issue_description}`, `{question}`) remain at invocation. Adding a new intent generally means adding a fourth template here.
- **`guardrails.py`** (Part B) — pure functions, no LLM calls. `education_injection_detector` is regex-based across 5 categories (`homework_fraud`, `academic_dishonesty`, `data_exfiltration`, `prompt_manipulation`, `scope_creep`); CRITICAL severity short-circuits the graph. `output_content_filter` runs after the LLM. `safe_learnsphere_invoke` is the end-to-end wrapper. `TEST_MATRIX` is the data behind `/api/test-matrix`.
- **`tools_agents.py`** (Part C) — `@tool`-decorated functions over in-memory dicts (`COURSE_CATALOG`, `ENROLLMENT_DATA`, `FAQ_DATABASE`) plus three **scoped** agents built via `create_tool_calling_agent` + `AgentExecutor(max_iterations=5)`. Each agent is restricted to a subset of tools — do not give an agent tools outside its scope (the scoping is the security boundary, not just an organizational choice).
- **`graph.py`** (Part D) — `LearnBotState` (TypedDict, 8 fields) is the state contract every node must respect. Routing happens via two **conditional edges** (declarative in the graph topology), not a router node — preserve this pattern when extending so the graph stays introspectable.
- **`main.py`** — thin FastAPI layer: validates with Pydantic, calls `run_learnbot`, flattens state into `ChatResponse`. Mock data (courses, FAQs) is exposed read-only via `GET /api/courses` and `GET /api/faqs` directly from `tools_agents` dicts.

## Config

`config.py` reads env vars via `python-dotenv`. Required: `GROQ_API_KEY`, `TAVILY_API_KEY`. Optional: `GROQ_MODEL` (default `llama-3.1-70b-versatile` in code, README mentions `llama3-70b-8192`), `HOST`, `PORT`. `PLATFORM_NAME` is hardcoded to `"LearnSphere"` and threaded into the prompt templates.

## Design constraints to preserve

These are explicitly called out as deliberate choices in `graph.py` reflection comments and the README — don't undo them without intent:

1. **TypedDict for state**, not plain dict — typo protection and LangGraph reducer semantics depend on it.
2. **Conditional edges, not a single router node** — branching must remain visible in the graph topology.
3. **Stateless per-request** — adding session memory means wiring a `MemorySaver`/`SqliteSaver` checkpointer with a `thread_id`, not mutating module-level state.
