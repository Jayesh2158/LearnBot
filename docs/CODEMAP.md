# CODEMAP.md

Code map of the workspace. Headers = workspace-relative path + recursive children count + short description. Lists immediate children files only. Excludes `.gitignore`'d paths (`node_modules/`, `venv/`, `.env`, `__pycache__/`, etc.) and `agents/TEMP/`.

## `/` (20) — flat project root with Python backend + React frontend

- `CLAUDE.md` — project guidance + Rosetta bootstrap section
- `README.md` — original project README (mentions backend/frontend split that does not match actual layout)
- `config.py` — env-driven `Settings` class
- `prompts.py` — three `ChatPromptTemplate`s for course/support/faq intents
- `guardrails.py` — regex injection detector + `TEST_MATRIX`
- `tools_agents.py` — `@tool` functions + three scoped LangChain agents
- `graph.py` — `LearnBotState` TypedDict + LangGraph `StateGraph`
- `main.py` — FastAPI app exposing `/api/*` endpoints
- `requirements.txt` — Python deps
- `package.json` — npm deps + scripts
- `package-lock.json` — npm lockfile
- `.env.example` — env template (commit-safe)
- `.gitignore` — VCS ignore list
- `.mcp.json` — Rosetta MCP server registration for Claude Code

## `/src` (3) — React frontend source

- `index.js` — React DOM entry point
- `App.js` — main UI component (chat surface)
- `styles/App.css` — single stylesheet

## `/public` (1) — CRA static root

- `index.html` — HTML shell for the React bundle

## `/docs` (6) — Rosetta-managed project documentation

- `CONTEXT.md` — business context
- `ARCHITECTURE.md` — architecture and technical requirements
- `TECHSTACK.md` — this file family
- `DEPENDENCIES.md` — direct dependency list
- `CODEMAP.md` — this file
- `ASSUMPTIONS.md` — assumptions & unknowns
- `TODO.md` — improvements and large TODOs
- `PATTERNS/INDEX.md` — pattern index (see below)

## `/docs/PATTERNS` (N) — extracted coding/architectural patterns

- `INDEX.md` — index of patterns
- `CHANGES.md` — change log
- _(one `.md` per extracted pattern; produced in Phase 5)_

## `/agents` (3) — Rosetta agent-managed state files (committed)

- `IMPLEMENTATION.md` — current implementation state
- `MEMORY.md` — error/recovery memory
- `init-workspace-flow-state.md` — last init-workspace-flow run state
- `TEMP/` — scratch (ignored by git)

## `/.claude` (70+) — Claude Code customization (Rosetta shells)

- `settings.local.json` — local Claude Code settings (ignored)
- `skills/` — 28 skill shells (each a `<name>/SKILL.md`)
- `agents/` — 9 agent shells (each a `<name>.md`)
- `commands/` — 34 workflow/command shells (each a `<name>.md`)

## Excluded from CODEMAP

- `node_modules/` — npm install tree
- `venv/` — Python virtualenv
- `.git/` — git internals
- `agents/TEMP/` — Rosetta scratch
- `.env` — secrets
