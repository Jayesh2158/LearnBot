# Pattern — `@tool` over in-memory dict

## What it solves

LearnBot uses mock data (no DB). Each domain dataset is a module-level dict, and a thin `@tool`-decorated function exposes a stable JSON-serializable lookup over it. The tool docstring becomes the LLM's tool description.

## When to use

- Adding a new tool that reads from a mock dataset.
- Promoting a dataset to a real datastore later — the call site keeps the same signature; replace the dict access with a query.

## Where it occurs

- [tools_agents.py:114](../../tools_agents.py) `get_course_info(course_id)` over `COURSE_CATALOG`.
- [tools_agents.py:143](../../tools_agents.py) `check_enrollment_status(student_id)` over `ENROLLMENT_DATA`.
- [tools_agents.py:177](../../tools_agents.py) `create_support_ticket(...)` (write-style mock).
- [tools_agents.py:223](../../tools_agents.py) `get_faq_answer(question)` over `FAQ_DATABASE`.

## Template

```python
MY_DATA = {
    "key1": {"field": "value", ...},
    ...
}

@tool
def lookup_thing(key: str) -> dict:
    """One-line description the LLM will read to decide whether to call this tool.

    Args:
        key: stable identifier for the record.

    Returns:
        Dict with `found` boolean + record fields, or an error message when missing.
    """
    record = MY_DATA.get(key)
    if not record:
        return {"found": False, "error": f"No record for {key!r}"}
    return {"found": True, **record}
```

## Extension points

- Move `MY_DATA` to its own file when the dataset grows past a few entries.
- Replace dict with DB query later — keep the return shape stable so the agent prompt and scope do not change.

## Pitfalls

- Do not return non-JSON-serializable objects from a `@tool` — the LangChain agent will fail to format the observation.
- Keep the docstring focused on "when to call" — the LLM uses it as the tool description.
