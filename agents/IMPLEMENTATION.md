# IMPLEMENTATION.md

Current state of implementation. Very brief. No change log here — see git history. DRY: every detail lives elsewhere; this is the index.

## Status

- **Backend:** complete and runnable. `uvicorn main:app --reload` from repo root.
- **Frontend:** complete and runnable. `npm install && npm start` from repo root.
- **Tests:** none — see [ARCHITECTURE.md#testing](../docs/ARCHITECTURE.md).
- **Rosetta workspace:** initialized 2026-05-18 via `init-workspace-flow`. See [init-workspace-flow-state.md](init-workspace-flow-state.md) for phase-by-phase status.

## What's wired

| Surface | State | Reference |
|---|---|---|
| `POST /api/chat` | end-to-end through LangGraph | [main.py](../main.py), [graph.py](../graph.py) |
| `POST /api/safety-check` | standalone guardrail | [main.py](../main.py), [guardrails.py](../guardrails.py) |
| `GET /api/courses` | mock dict dump | [main.py](../main.py), [tools_agents.py](../tools_agents.py) |
| `GET /api/faqs` | mock dict dump | [main.py](../main.py), [tools_agents.py](../tools_agents.py) |
| `GET /api/graph-info` | graph metadata | [main.py](../main.py) |
| `GET /api/test-matrix` | descriptive test data | [main.py](../main.py), [guardrails.py](../guardrails.py) |
| `GET /api/health` | liveness | [main.py](../main.py) |
| Three scoped agents | course / support / faq | [tools_agents.py](../tools_agents.py) |
| Regex guardrail | 5 categories | [guardrails.py](../guardrails.py) |
| React chat UI | single component | [src/App.js](../src/App.js) |

## What's not wired

- No persistence layer; all data is in-memory dicts.
- No conversation memory across `/api/chat` calls (intentional — see [ARCHITECTURE.md](../docs/ARCHITECTURE.md) constraint #3).
- No authentication / authorization / rate limiting.
- No CI, no linter config, no test runner.
