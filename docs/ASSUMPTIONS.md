# ASSUMPTIONS.md

Assumptions and unknowns gathered during `init-workspace-flow`. Each entry: assumption / confidence / target file when resolved. Resolve in Phase 7 (questions) or as the work that uncovers the answer happens.

| # | Assumption | Confidence | Target when resolved |
|---|---|---|---|
| 1 | ~~README's `backend/` and `frontend/` directory references are stale~~ **Resolved 2026-05-18 (Phase 7):** README updated to describe the flat layout and root-level commands. | Resolved | [README.md](../README.md) |
| 2 | ~~`GROQ_MODEL` defaults to `llama-3.1-70b-versatile`; README mentioned `llama3-70b-8192`~~ **Resolved 2026-05-19:** the 3.1 model was decommissioned by Groq. Code, README, `.env`, and `.env.example` all now use `llama-3.3-70b-versatile`. | Resolved | — |
| 3 | ~~Tavily search is a declared dependency but no node invokes it~~ **Resolved 2026-05-18 (Phase 7):** confirmed dead code, removed from `requirements.txt`, `config.py`, `.env.example`, and `/api/health`. | Resolved | — |
| 4 | "Test matrix" at `/api/test-matrix` is descriptive only — no plan to convert it into an executable suite as part of this init. | Medium | [ARCHITECTURE.md#testing](ARCHITECTURE.md) |
| 5 | Stateless-per-request is a deliberate choice, not a missing-feature. Adding memory means wiring a checkpointer; see constraint #3 in [ARCHITECTURE.md](ARCHITECTURE.md). | High | resolved in [ARCHITECTURE.md](ARCHITECTURE.md) |
| 6 | ~~`mcp/rosetta.json` is a redundant copy of `.mcp.json`~~ **Resolved 2026-05-19:** `mcp/rosetta.json` (+ empty `mcp/` dir) deleted. `.mcp.json` is canonical. | Resolved | — |
| 7 | `node_modules/` and `venv/` are user-managed reinstalls (gitignored, present in current checkout). Init does not touch them. | High | resolved here |
| 8 | The mock data sizes (`COURSE_CATALOG`, `ENROLLMENT_DATA`, `FAQ_DATABASE`) are small enough to live in-memory indefinitely for the demo's lifetime. | High | resolved here |
| 9 | The CLAUDE.md "broken lockfile" note ("react-scripts: 0.0.0 stub") was a transient issue and the current `package-lock.json` is healthy. | Medium | resolved by next `npm install` if regressed |
| 10 | The `agents/` folder name is overloaded — Rosetta uses it for workflow state (e.g. `IMPLEMENTATION.md`), while the codebase also speaks of LangChain "agents" (course/support/faq). Not a conflict, but worth flagging for readers. | High | [AGENT MEMORY.md](../agents/MEMORY.md) — note for new contributors |
