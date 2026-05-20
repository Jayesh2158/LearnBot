# TODO.md

Improvements, suggestions, and large TODOs surfaced by `init-workspace-flow`. Not a sprint backlog — these are durable observations to revisit.

## Backend

- ~~**Wire Tavily search or remove it.**~~ Resolved 2026-05-18: removed (Tavily was dead code).
- ~~**Reconcile `mcp/rosetta.json` and `.mcp.json`.**~~ Resolved 2026-05-19: `mcp/rosetta.json` deleted (byte-identical duplicate). `.mcp.json` is the single source of truth.
- **Decide on a test runner.** No `pytest`, no `npm test`. If real tests are wanted, pick a runner and seed a smoke test for `POST /api/chat`. See [ARCHITECTURE.md#testing](ARCHITECTURE.md).
- ~~**Reconcile `GROQ_MODEL` defaults.**~~ Resolved 2026-05-19: bumped everywhere to `llama-3.3-70b-versatile` after Groq decommissioned `llama-3.1-70b-versatile`.

## Documentation

- ~~**Update the README** to drop the `backend/` / `frontend/` split~~ Resolved 2026-05-18: README rewritten to describe flat layout.
- **Add a `docs/REQUIREMENTS/INDEX.md`** if/when original requirements (course catalog, FAQ list, intent definitions) are formalized — Rosetta has a slot for it but this repo has not authored requirements yet.

## Frontend

- **No `npm test` script** is declared. Add one (or remove the assumption that `react-scripts` ships one) if frontend tests get added.
- **`src/styles/App.css` is the only stylesheet.** If the UI grows, consider component-scoped CSS or a styling solution before it becomes monolithic.

## Rosetta workspace hygiene

- **Start a new Claude Code session** before relying on the new shells in `.claude/` (per Phase 8 verification). Shells take effect at session start.
- **Delete `init-rosetta-shells-flow.md`** if it exists from a prior init (it doesn't in this repo, but Phase 8 instructs the check).
