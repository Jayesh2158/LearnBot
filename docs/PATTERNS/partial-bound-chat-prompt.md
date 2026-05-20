# Pattern — Partial-bound `ChatPromptTemplate`

## What it solves

LangChain `ChatPromptTemplate`s mix two kinds of variables: configuration values that are constant per process (platform name, date) and per-call inputs (user query, issue description). Pre-binding the constants via `.partial(...)` means the invocation site only supplies the dynamic vars — fewer mistakes, easier to read.

## When to use

- Adding a new intent template in [prompts.py](../../prompts.py).
- Any prompt that has a clear split between "set once at startup" and "per request".

## Where it occurs

- [prompts.py](../../prompts.py) — three templates (course, support, faq), each created with `ChatPromptTemplate.from_messages(...)` then exposed via `get_partial_templates(platform_name=...)` which calls `.partial(platform_name=..., current_date=...)`.

## Template

```python
from langchain_core.prompts import ChatPromptTemplate
from datetime import date

_MY_INTENT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", "You are the {platform_name} <Role>. Today is {current_date}. Be brief."),
    ("human", "{query}"),
])

def get_partial_templates(platform_name: str = "LearnSphere"):
    today = date.today().isoformat()
    return {
        "my_intent": _MY_INTENT_TEMPLATE.partial(
            platform_name=platform_name,
            current_date=today,
        ),
    }

# Invocation site:
template = get_partial_templates()["my_intent"]
prompt = template.format(query="...")   # only the dynamic var remains
```

## Extension points

- Add new intents by extending `get_partial_templates`'s return dict.
- When a constant graduates from "set at startup" to "per request" (e.g. tenant-aware), remove it from `.partial` and pass it at format time.

## Pitfalls

- Do not call `.partial` inside the request handler — bind once at module/startup scope.
- Mixing `{platform_name}` and `{query}` placeholders without `.partial` means callers must always pass `platform_name` — the whole point of this pattern is to avoid that.
