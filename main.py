"""
╔══════════════════════════════════════════════════════════════════╗
║  LearnBot — FastAPI Backend                                     ║
║  Full-Stack Conversational AI for LearnSphere                   ║
╚══════════════════════════════════════════════════════════════════╝

REST API exposing:
  POST /api/chat          — Main chat endpoint (runs LangGraph workflow)
  POST /api/safety-check  — Standalone safety check
  GET  /api/courses       — List available courses
  GET  /api/health        — Health check
  GET  /api/graph-info    — Graph architecture metadata
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import time

from config import settings
from guardrails import education_injection_detector, output_content_filter, TEST_MATRIX
from tools_agents import COURSE_CATALOG, FAQ_DATABASE
from graph import run_learnbot

# ─────────────────────────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="LearnBot API",
    description="LearnSphere Conversational AI Backend — Capstone Q3",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────
# Request / Response Models
# ─────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000,
                         description="The student's message")
    student_name: Optional[str] = Field(default="Student",
                                         description="Student's display name")


class ChatResponse(BaseModel):
    status: str
    response: str
    intent: Optional[str]
    safety_status: str
    safety_flags: list
    tool_calls_made: list
    processing_time_ms: float
    agent_used: Optional[str]


class SafetyCheckRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class SafetyCheckResponse(BaseModel):
    flagged: bool
    flags: list
    highest_severity: str
    should_block: bool


# ─────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "LearnBot API",
        "version": "1.0.0",
        "model": settings.GROQ_MODEL,
        "groq_configured": bool(settings.GROQ_API_KEY),
        "tavily_configured": bool(settings.TAVILY_API_KEY)
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint. Runs the full LangGraph workflow:
    receive_input → safety_check → intent_classifier → agent_handler → response
    """
    start = time.time()

    try:
        result = await run_learnbot(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")

    elapsed = (time.time() - start) * 1000
    metadata = result.get("processing_metadata", {})

    return ChatResponse(
        status="success" if result.get("safety_status") == "safe" else result.get("safety_status", "unknown"),
        response=result.get("agent_response", "No response generated."),
        intent=result.get("intent"),
        safety_status=result.get("safety_status", "unknown"),
        safety_flags=result.get("safety_flags", []),
        tool_calls_made=result.get("tool_calls_made", []),
        processing_time_ms=round(elapsed, 2),
        agent_used=metadata.get("agent_used")
    )


@app.post("/api/safety-check", response_model=SafetyCheckResponse)
async def safety_check(request: SafetyCheckRequest):
    """Standalone safety check — tests input without invoking agents."""
    result = education_injection_detector(request.text)
    return SafetyCheckResponse(**result)


@app.get("/api/courses")
async def list_courses():
    """Return the course catalog."""
    return {
        "courses": [
            {"id": cid, **info}
            for cid, info in COURSE_CATALOG.items()
        ]
    }


@app.get("/api/faqs")
async def list_faqs():
    """Return the FAQ database."""
    return {
        "faqs": [
            {"id": key, "question": faq["question"], "answer": faq["answer"]}
            for key, faq in FAQ_DATABASE.items()
        ]
    }


@app.get("/api/graph-info")
async def graph_info():
    """Return graph architecture metadata."""
    return {
        "nodes": [
            "receive_input", "safety_check", "rejection_handler",
            "intent_classifier", "course_handler", "support_handler", "faq_handler"
        ],
        "edges": [
            {"from": "receive_input", "to": "safety_check", "type": "unconditional"},
            {"from": "safety_check", "to": "intent_classifier", "type": "conditional", "condition": "safe"},
            {"from": "safety_check", "to": "rejection_handler", "type": "conditional", "condition": "unsafe"},
            {"from": "intent_classifier", "to": "course_handler", "type": "conditional", "condition": "course"},
            {"from": "intent_classifier", "to": "support_handler", "type": "conditional", "condition": "support"},
            {"from": "intent_classifier", "to": "faq_handler", "type": "conditional", "condition": "faq"},
            {"from": "rejection_handler", "to": "END", "type": "unconditional"},
            {"from": "course_handler", "to": "END", "type": "unconditional"},
            {"from": "support_handler", "to": "END", "type": "unconditional"},
            {"from": "faq_handler", "to": "END", "type": "unconditional"},
        ],
        "state_fields": [
            "messages", "user_input", "intent", "safety_status",
            "safety_flags", "agent_response", "tool_calls_made",
            "processing_metadata"
        ]
    }


@app.get("/api/test-matrix")
async def get_test_matrix():
    """Return the safety test matrix for the frontend test panel."""
    return TEST_MATRIX


# ─────────────────────────────────────────────────────────────────
# Run
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
