# ARCHITECTURE.md

Architecture and technical requirements. No business context — see [CONTEXT.md](CONTEXT.md). For the file/folder map see [CODEMAP.md](CODEMAP.md), for the stack see [TECHSTACK.md](TECHSTACK.md), for recurring code shapes see [PATTERNS/INDEX.md](PATTERNS/INDEX.md).

This file is self-defined: every entry describes a structural or behavioral fact about the implementation, not the product motivation.

## Workspace structure

Single flat repo at root. Python backend modules + React CRA frontend live side by side. README mentions `backend/`/`frontend/` directories that **do not exist** — run all commands from the repo root.

```
.                                  ← repo root
├── config.py                      ← Settings (env-driven)
├── prompts.py                     ← ChatPromptTemplates per intent
├── guardrails.py                  ← Regex injection detector + TEST_MATRIX
├── tools_agents.py                ← @tool fns + 3 scoped agents
├── graph.py                       ← LearnBotState + LangGraph StateGraph
├── main.py                        ← FastAPI app
├── requirements.txt
├── package.json                   ← React CRA
├── src/                           ← React frontend
├── public/
├── docs/                          ← Rosetta docs (this file family)
├── agents/                        ← Rosetta agent state (IMPLEMENTATION, MEMORY, …)
├── .claude/                       ← Rosetta Claude Code shells
└── .mcp.json                      ← Rosetta MCP server registration
```

## Modules (backend)

Strict layering — keep these boundaries when editing.

### `config.py`

- Reads env vars via `python-dotenv`.
- Required: `GROQ_API_KEY`.
- Optional: `GROQ_MODEL` (default `llama-3.3-70b-versatile`), `HOST`, `PORT`.
- `PLATFORM_NAME` is hardcoded to `"LearnSphere"` and threaded into prompt templates.

### `prompts.py` — "Part A"

- Three `ChatPromptTemplate`s, each pre-bound with `.partial(platform_name=..., current_date=...)`.
- Only dynamic vars (`{query}`, `{issue_description}`, `{question}`) remain at invocation time.
- Pattern: [partial-bound-chat-prompt](PATTERNS/partial-bound-chat-prompt.md).
- Adding a new intent generally adds a fourth template here.

### `guardrails.py` — "Part B"

- Pure functions, **no LLM calls**.
- `education_injection_detector(text)` — regex-based across 5 categories: `homework_fraud`, `academic_dishonesty`, `data_exfiltration`, `prompt_manipulation`, `scope_creep`. CRITICAL severity short-circuits the graph.
- `output_content_filter(response)` — runs after the LLM.
- `safe_learnsphere_invoke(...)` — end-to-end wrapper combining the above.
- `TEST_MATRIX` — the data behind `GET /api/test-matrix`.
- Pattern: [regex-guardrail-structured-result](PATTERNS/regex-guardrail-structured-result.md).

### `tools_agents.py` — "Part C"

- `@tool`-decorated functions over in-memory dicts: `COURSE_CATALOG`, `ENROLLMENT_DATA`, `FAQ_DATABASE`.
- Three scoped agents via `create_tool_calling_agent` + `AgentExecutor(max_iterations=5)`.
- Each agent is **restricted to a subset of tools** — the scoping is the security boundary, not just organization.
- Patterns: [scoped-tool-calling-agent](PATTERNS/scoped-tool-calling-agent.md), [tool-over-in-memory-dict](PATTERNS/tool-over-in-memory-dict.md).

### `graph.py` — "Part D"

- `LearnBotState` (TypedDict, 8 fields) — the state contract every node must respect.
- Routing happens via two **conditional edges** (declarative in the graph topology), not a router node.
- Patterns: [typed-dict-graph-state](PATTERNS/typed-dict-graph-state.md), [conditional-edge-router](PATTERNS/conditional-edge-router.md).

### `main.py`

- Thin FastAPI layer: validates with Pydantic, calls `run_learnbot`, flattens state into `ChatResponse`.
- Mock data (courses, FAQs) is exposed read-only via `GET /api/courses` and `GET /api/faqs` directly from `tools_agents` dicts.
- Pattern: [fastapi-endpoint-pydantic-io](PATTERNS/fastapi-endpoint-pydantic-io.md).

## Request flow

Single-turn, stateless per request — each `/api/chat` call runs a fresh LangGraph traversal.

```
FastAPI (main.py)
  └─ run_learnbot(message) → LangGraph StateGraph (graph.py)
      receive_input
        └─ safety_check                              (guardrails.education_injection_detector)
             ├─ unsafe  → rejection_handler  → END
             └─ safe    → intent_classifier
                            ├─ course   → course_handler   (tools_agents.get_course_agent)
                            ├─ support  → support_handler  (tools_agents.get_support_agent)
                            └─ faq      → faq_handler      (tools_agents.get_faq_agent)
                                            └─ → END
```

## Frontend

- React 18, standard Create React App layout (`public/index.html`, `src/index.js`, `src/App.js`, `src/styles/App.css`).
- Single chat surface; POSTs to `/api/chat`. Dev server proxies to `http://localhost:8000` via `"proxy"` in [package.json](../package.json).

## Testing

- **No executable test runner** is configured (no `pytest`, no `npm test` script).
- The "test matrix" is descriptive data exposed at `GET /api/test-matrix` (see [guardrails.py](../guardrails.py)). It documents intended detection behavior; it does not run anything.
- Adding tests means choosing and wiring a runner (decision deferred — see [ASSUMPTIONS.md](ASSUMPTIONS.md)).

## Build & run

See top of [CLAUDE.md](../CLAUDE.md) for the canonical commands. All commands run from repo root despite the README's `cd backend` / `cd frontend` references.

## Design constraints to preserve

These are deliberate, called out in code comments and CLAUDE.md. Don't undo without intent.

1. **TypedDict for state**, not plain dict — typo protection + LangGraph reducer semantics.
2. **Conditional edges, not a router node** — branching must remain visible in the graph topology.
3. **Stateless per-request** — adding session memory means wiring a `MemorySaver`/`SqliteSaver` checkpointer with a `thread_id`, not mutating module-level state.
4. **Agent tool scoping is the security boundary** — never give an agent a tool outside its intent.
5. **Guardrails contain zero LLM calls** — preserves the determinism and zero-cost gate before any model invocation.
