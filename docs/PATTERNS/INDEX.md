# PATTERNS/INDEX.md

Index of coding and architectural patterns extracted from this workspace. Each pattern is genuine and recurring (2+ occurrences) — apply when you'd otherwise reinvent it.

| # | Pattern | One-line description |
|---|---|---|
| 1 | [TypedDict graph state with partial-update nodes](typed-dict-graph-state.md) | Define `LearnBotState` once; every node returns only the fields it modifies. |
| 2 | [Conditional-edge router function](conditional-edge-router.md) | A pure function reads state, returns a string label, graph maps label → node. |
| 3 | [Scoped tool-calling agent factory](scoped-tool-calling-agent.md) | `_build_agent(tools, prompt)` returns an `AgentExecutor` restricted to a specific tool subset. |
| 4 | [@tool over in-memory dict](tool-over-in-memory-dict.md) | LangChain `@tool` wraps a dict lookup with a stable JSON response shape. |
| 5 | [FastAPI endpoint + Pydantic IO models](fastapi-endpoint-pydantic-io.md) | Each route declares paired `*Request`/`*Response` Pydantic models. |
| 6 | [Partial-bound ChatPromptTemplate](partial-bound-chat-prompt.md) | Templates are pre-bound with `.partial(...)` so only dynamic vars remain at invocation. |
| 7 | [Regex-category guardrail returning structured result](regex-guardrail-structured-result.md) | Pure functions over `{category: [regex,...]}` returning `{safe, flags, severity}`. |
