# CONTEXT.md

Business and overall context for this workspace. Target state only — no change log, no technical details, no explanation of changes. For architecture see [ARCHITECTURE.md](ARCHITECTURE.md).

This file is self-defined: every entry describes a stakeholder-level fact about the product, not its implementation.

## Product

- **Name:** LearnBot — a single-turn conversational assistant for the **LearnSphere** educational platform.
- **Surface:** A React chat web UI talks to a FastAPI backend at `/api/chat`. Swagger UI is available at `/docs`.
- **Position:** Demo / training reference for building safe, scoped LLM agents inside a curriculum context. Not a production-grade student-facing service.

## Purpose

- Help LearnSphere students with three distinct intents:
  - **course** — explore the catalog, check prerequisites, confirm enrollment status.
  - **support** — resolve account/technical issues, file a support ticket when the FAQ is insufficient.
  - **faq** — answer frequently asked questions about the platform.
- Demonstrate explicit safety guardrails around an LLM-backed support flow: detect homework-fraud / academic-dishonesty / prompt-injection attempts and short-circuit the response.

## Domain

- **Users:** LearnSphere students; secondarily, support staff who'd inherit a ticket.
- **Data:** Mock courses, mock enrollments, mock FAQs — all in-memory dicts in [tools_agents.py](../tools_agents.py). No real PII flows through the system.
- **Trust model:** student input is untrusted; each intent's agent is restricted to a minimal tool set so even a successful prompt injection has a narrow blast radius.

## Goals (target state)

- A student types one message → safe, scoped, on-topic response within ~2s.
- Anything that looks like cheating, prompt manipulation, or data exfiltration is rejected before any LLM call is made.
- Course / support / FAQ each have their own prompt persona and their own tool surface; no agent gets tools outside its scope.

## Non-goals

- Multi-turn conversation memory (system is stateless per request by design — see [ARCHITECTURE.md](ARCHITECTURE.md) "Stateless per-request").
- Hitting a real LMS, ticketing system, or analytics backend — all data is mocked.
- Authentication, authorization, rate limiting, or tenant isolation.
- An executable test suite — the "test matrix" exposed at `GET /api/test-matrix` is descriptive data, not a runner.

## Stakeholders

- **Curriculum / demo author** — owns the LearnSphere narrative and which intents matter.
- **Backend developer** — owns the FastAPI + LangGraph + LangChain stack.
- **Frontend developer** — owns the React chat UI.
- **Safety reviewer** — owns the regex guardrail categories in [guardrails.py](../guardrails.py) and the `TEST_MATRIX`.
