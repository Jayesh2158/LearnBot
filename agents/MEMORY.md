# AGENT MEMORY

Generalized reusable lessons from agent sessions in this workspace. Root causes converted into preventive rules, not incident-specific notes. Entries are h3 headers with `[ACTIVE|RETIRED]` status. Brief, grep-friendly, MECE across sections.

## Preventive Rules

### Always run from the repo root, never `cd backend` or `cd frontend` [ACTIVE]
- The README mentions a `backend/`/`frontend/` split that does not match the actual flat layout.
- All Python files and the React CRA project live at the repo root. See [CODEMAP.md](../docs/CODEMAP.md).

### Never give a scoped agent a tool outside its intent [ACTIVE]
- The tool-set passed to `create_tool_calling_agent` is the security boundary, not just organization.
- See [PATTERNS/scoped-tool-calling-agent.md](../docs/PATTERNS/scoped-tool-calling-agent.md).

### Never call an LLM from a guardrail [ACTIVE]
- Guardrails must be pure functions returning `{safe, flags, severity}`. Defeating determinism breaks the zero-cost gate.
- See [PATTERNS/regex-guardrail-structured-result.md](../docs/PATTERNS/regex-guardrail-structured-result.md).

### Adding a new state field means updating `LearnBotState` first [ACTIVE]
- Nodes return partial dicts; the TypedDict is the schema. Adding a field elsewhere first will silently fail typo protection.
- See [PATTERNS/typed-dict-graph-state.md](../docs/PATTERNS/typed-dict-graph-state.md).

### Adding session memory ≠ mutating module-level state [ACTIVE]
- Wire a `MemorySaver` or `SqliteSaver` checkpointer with a `thread_id`. See constraint #3 in [ARCHITECTURE.md](../docs/ARCHITECTURE.md).

## What Worked

### `parallel_tool_calls=False` for Groq + Llama 3.x [ACTIVE]
- Groq returns `tool_use_failed: Failed to call a function. Please adjust your prompt.` whenever Llama 3.x emits a parallel tool call. Setting `model_kwargs={"parallel_tool_calls": False}` on `ChatGroq` in [tools_agents.py:get_llm()](../tools_agents.py) reduces but does not eliminate it.

### Retry once on `tool_use_failed` [ACTIVE]
- Even with `parallel_tool_calls=False`, Groq + Llama 3.x still flakes ~10–20% of the time. `_ainvoke_with_retry` in [graph.py](../graph.py) catches exceptions whose text contains `tool_use_failed` or `Failed to call a function` and re-runs the agent once on a fresh instance. Empirical: 5/5 success rate after this combined with tightened tool-usage rules in agent prompts.
- The two fixes are complementary — keep both. Disabling parallel calls reduces the rate; the retry mops up the rest.

## What Failed

_(empty — populate after lessons accumulate in real sessions)_

## Discoveries

### `agents/` folder name is overloaded [ACTIVE]
- Rosetta uses `agents/` for workflow state (`IMPLEMENTATION.md`, `MEMORY.md`, `init-workspace-flow-state.md`).
- The codebase also has LangChain "agents" (course/support/faq) in [tools_agents.py](../tools_agents.py).
- No technical conflict — but flag it for new contributors who'll see both meanings in the same repo.

### `mcp/rosetta.json` duplicates `.mcp.json` [RETIRED]
- Resolved 2026-05-19: `mcp/rosetta.json` deleted; `.mcp.json` is the single canonical Rosetta MCP server config.
