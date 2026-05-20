# Pattern — TypedDict graph state with partial-update nodes

## What it solves

Multi-node LangGraph workflows need an explicit state contract that survives partial updates from each node without losing other fields. Plain dicts make typos silent; full-state returns make node logic verbose and error-prone.

## When to use

- Adding a new node to [graph.py](../../graph.py).
- Introducing a new field to the state — add it once to `LearnBotState`, then any node may emit it in its partial return.

## Where it occurs

- `LearnBotState` declared in [graph.py:44](../../graph.py).
- Every node function (`receive_input`, `safety_check`, `intent_classifier`, `rejection_handler`, the three `*_handler` nodes) returns a **partial dict** — only the fields it changes. LangGraph merges via reducer semantics.

## Template

```python
from typing import TypedDict, Optional
from langgraph.graph import StateGraph

class LearnBotState(TypedDict):
    messages: list                # append-only list (use reducer)
    user_input: str
    intent: Optional[str]
    safety_status: str            # safe | unsafe | review_needed
    safety_flags: list
    agent_response: Optional[str]
    tool_calls_made: list
    processing_metadata: dict


def my_node(state: LearnBotState) -> dict:
    """Return ONLY the fields this node modifies. LangGraph merges with existing state."""
    # ... compute …
    return {
        "intent": "course",                       # field this node sets
        "tool_calls_made": state["tool_calls_made"] + ["classifier"],  # append-style update
    }
```

## Extension points

- New fields: extend `LearnBotState` first, then start emitting them from the node that produces them.
- Reducer semantics: for fields that need merge (e.g. `messages` append-only), wire a reducer when adding the field.

## Pitfalls

- Returning the full state from a node is allowed but defeats the partial-update intent and obscures which node owns which field.
- Never use a plain `dict` instead of `TypedDict` — losing typo protection is the explicit anti-goal.
