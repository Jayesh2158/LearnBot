# Pattern — FastAPI endpoint with Pydantic IO models

## What it solves

Every API route declares a paired `<Name>Request` and `<Name>Response` Pydantic model. Validation happens at the boundary, and the response model both shapes the JSON and feeds the OpenAPI/Swagger docs at `/docs`.

## When to use

- Any new `@app.post(...)` or `@app.get(...)` that carries structured input or output.
- Read-only routes returning ad-hoc shapes (e.g. `/api/courses`) can stay schema-less, but anything the frontend depends on should get a model.

## Where it occurs

- [main.py:49](../../main.py) `ChatRequest` / [main.py:56](../../main.py) `ChatResponse` for `POST /api/chat`.
- [main.py:67](../../main.py) `SafetyCheckRequest` / [main.py:71](../../main.py) `SafetyCheckResponse` for `POST /api/safety-check`.

## Template

```python
from pydantic import BaseModel, Field
from typing import Optional

class MyRequest(BaseModel):
    field: str = Field(..., description="Human-readable description; surfaces in Swagger.")

class MyResponse(BaseModel):
    status: str
    result: Optional[str] = None

@app.post("/api/my-endpoint", response_model=MyResponse)
async def my_endpoint(request: MyRequest):
    """One-line summary. FastAPI uses this in the Swagger UI."""
    # ... call into business logic …
    return MyResponse(status="success", result="…")
```

## Extension points

- Reuse a `BaseModel` across endpoints when the shape is identical. Do not subclass just to rename — duplication is fine for paired IO models.
- Wrap the business call in a `try` and raise `HTTPException(500, detail=...)` when the failure is a server error (the existing `/api/chat` does this).

## Pitfalls

- Do not put validation inside the route body — let Pydantic handle it at the boundary.
- Keep the `response_model` honest: if the route returns extra fields, they will be dropped silently.
