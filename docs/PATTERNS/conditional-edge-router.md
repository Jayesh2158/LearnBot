# Pattern — Conditional-edge router function

## What it solves

Branching in a LangGraph should remain visible in the graph topology, not hidden inside a "router node" that re-runs logic. Conditional edges + a small router function expose the branch declaratively.

## When to use

- Any new fork in the request pipeline (safety gate, intent split, fallback handling).

## Where it occurs

- [graph.py:118](../../graph.py) `safety_router(state) -> str` — returns `"unsafe"` or `"safe"`.
- [graph.py:217](../../graph.py) `intent_router(state) -> str` — returns `"course"`, `"support"`, or `"faq"`.

Both are wired via `add_conditional_edges(source_node, router_fn, {label: target_node})` in `build_learnbot_graph()`.

## Template

```python
def my_router(state: LearnBotState) -> str:
    """Pure function: read state, return a label. NO side effects, NO LLM calls."""
    if state.get("safety_status") == "unsafe":
        return "unsafe"
    return "safe"

# In build_learnbot_graph():
graph.add_conditional_edges(
    "safety_check",
    my_router,
    {
        "safe":   "intent_classifier",
        "unsafe": "rejection_handler",
    },
)
```

## Extension points

- New labels: extend the router return values **and** the destination map together.
- Multi-criteria routing: keep the function pure; if it grows past ~10 lines, extract the decision into the upstream node and route on a single field.

## Pitfalls

- Do not introduce a "router node" that does routing inside its body — branching becomes invisible in the graph.
- Routers must be deterministic: same state → same label.
