# Pattern — Regex-category guardrail returning structured result

## What it solves

LearnBot's safety layer must be deterministic, fast, and free of LLM calls (no token cost, no latency, no model drift). Guardrails are pure functions that run a `{category: [regex,...]}` table against text and return a structured result downstream code can branch on.

## When to use

- Adding a new injection category (e.g. PII exfiltration).
- Adding a new post-LLM content filter.
- Any decision point where determinism and zero-LLM cost matter.

## Where it occurs

- [guardrails.py:89](../../guardrails.py) `education_injection_detector(text)` — 5 categories (`homework_fraud`, `academic_dishonesty`, `data_exfiltration`, `prompt_manipulation`, `scope_creep`); CRITICAL severity short-circuits the graph.
- [guardrails.py:150](../../guardrails.py) `output_content_filter(response)` — post-LLM filter with the same return shape.

## Template

```python
import re

MY_PATTERNS = {
    "category_a": {
        "patterns": [
            r"(?i)\b(do my homework|write my essay)\b",
            r"(?i)\b(complete\s+the\s+assignment)\b",
        ],
        "severity": "CRITICAL",
    },
    "category_b": {
        "patterns": [r"(?i)\bignore\s+previous\s+instructions\b"],
        "severity": "HIGH",
    },
}

def my_detector(text: str) -> dict:
    """Pure function. Returns: {safe, flags, severity, blocked}."""
    flags = []
    max_severity = "NONE"
    for category, cfg in MY_PATTERNS.items():
        for pat in cfg["patterns"]:
            if re.search(pat, text):
                flags.append({"category": category, "pattern": pat, "severity": cfg["severity"]})
                if SEVERITY_RANK[cfg["severity"]] > SEVERITY_RANK[max_severity]:
                    max_severity = cfg["severity"]
    return {
        "safe": max_severity not in {"CRITICAL", "HIGH"},
        "flags": flags,
        "severity": max_severity,
        "blocked": max_severity == "CRITICAL",
    }
```

## Extension points

- New category: append a key to the dict, set its `severity`.
- Multilingual: add Unicode-aware regexes; keep the same return shape so downstream routing logic does not change.

## Pitfalls

- Do not call an LLM from a guardrail — defeats the determinism guarantee.
- Do not return a bare boolean — downstream code (and `TEST_MATRIX` introspection at `/api/test-matrix`) depends on the structured `{safe, flags, severity}` shape.
