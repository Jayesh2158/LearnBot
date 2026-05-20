"""
╔══════════════════════════════════════════════════════════════════╗
║  PART D — LangGraph Workflow Architecture                       ║
║  LearnBot Capstone · LearnSphere Platform                       ║
╚══════════════════════════════════════════════════════════════════╝

Implements:
  D.1 — LearnBotState (TypedDict with 8 fields) + receive_input + safety_check
  D.2 — Conditional edge: safe → intent_classifier | unsafe → rejection_handler
  D.3 — intent_classifier node + 3-way routing
  D.4 — Handler nodes (course / support / faq) → END
  D.5 — Graph compilation + Mermaid export
  D.6 — Design reflection comments

State flows through 6 nodes with 2 conditional edges.
"""

import time
from typing import TypedDict, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from guardrails import education_injection_detector, output_content_filter
from tools_agents import get_course_agent, get_support_agent, get_faq_agent


# ═════════════════════════════════════════════════════════════════
# D.1 — LearnBotState TypedDict
# ═════════════════════════════════════════════════════════════════

# REFLECTION: Why TypedDict over a plain dict for state?
#
# TypedDict provides compile-time type checking and IDE auto-completion,
# making the 8-field state self-documenting. Unlike a plain dict where
# any key is valid and typos silently create new fields, TypedDict
# enforces the schema — if a node writes to "saftey_status" (typo),
# type checkers catch it. LangGraph also uses TypedDict to determine
# which fields to persist and which support "reducer" semantics
# (like append-only for messages). This is critical for stateful,
# multi-node graphs where debugging state corruption is costly.

class LearnBotState(TypedDict):
    messages: list               # Full conversation history (append-only)
    user_input: str              # Current raw user message
    intent: Optional[str]        # Classified intent: course / support / faq
    safety_status: str           # safe | unsafe | review_needed
    safety_flags: list           # Detected injection patterns with severity
    agent_response: Optional[str]  # Final response from routed agent
    tool_calls_made: list        # Ordered list of tool names invoked
    processing_metadata: dict    # Timestamps, token counts, agent_used


# ═════════════════════════════════════════════════════════════════
# NODE 1 — receive_input
# ═════════════════════════════════════════════════════════════════

def receive_input(state: LearnBotState) -> dict:
    """
    Parse user message, initialize state fields, log entry timestamp.
    """
    return {
        "messages": state.get("messages", []) + [HumanMessage(content=state["user_input"])],
        "intent": None,
        "safety_status": "pending",
        "safety_flags": [],
        "agent_response": None,
        "tool_calls_made": [],
        "processing_metadata": {
            "entry_timestamp": datetime.now().isoformat(),
            "agent_used": None,
            "total_tokens": 0
        }
    }


# ═════════════════════════════════════════════════════════════════
# NODE 2 — safety_check
# ═════════════════════════════════════════════════════════════════

def safety_check(state: LearnBotState) -> dict:
    """
    Run education_injection_detector on user input.
    Populates safety_status and safety_flags.
    """
    detection = education_injection_detector(state["user_input"])

    if detection["should_block"]:
        status = "unsafe"
    elif detection["flagged"]:
        status = "review_needed"
    else:
        status = "safe"

    return {
        "safety_status": status,
        "safety_flags": detection["flags"]
    }


# ═════════════════════════════════════════════════════════════════
# D.2 — Safety routing function
# ═════════════════════════════════════════════════════════════════

# REFLECTION: Why conditional edges over a single router node?
#
# Conditional edges keep routing logic DECLARATIVE — the graph
# definition itself shows the branching, making it inspectable,
# testable, and visualizable in Mermaid diagrams. A monolithic
# router node hides routing in imperative code, making the graph
# opaque. Conditional edges also let LangGraph optimize execution:
# it can pre-compute valid paths, validate the graph at compile
# time (no dead-end nodes), and parallelize independent branches.
# For LearnBot, the 2-stage conditional (safety → intent) creates
# a clear pipeline visible in the graph diagram itself.

def safety_router(state: LearnBotState) -> str:
    """Route based on safety check result."""
    if state["safety_status"] == "safe" or state["safety_status"] == "review_needed":
        return "intent_classifier"
    return "rejection_handler"


# ═════════════════════════════════════════════════════════════════
# REJECTION HANDLER
# ═════════════════════════════════════════════════════════════════

def rejection_handler(state: LearnBotState) -> dict:
    """Return appropriate refusal message for unsafe inputs."""
    flags = state.get("safety_flags", [])
    categories = set(f.get("category", "") for f in flags)

    if "data_exfiltration" in categories:
        msg = ("🔒 Access denied. I cannot provide bulk student data, grades, "
               "or database access. This request has been logged.")
    elif "prompt_manipulation" in categories:
        msg = ("🛡️ I detected an attempt to modify my instructions. "
               "I can only assist with LearnSphere-related education queries.")
    elif "academic_dishonesty" in categories:
        msg = ("📚 I'm committed to academic integrity and cannot assist with "
               "cheating, plagiarism, or bypassing assessment safeguards.")
    else:
        msg = ("⚠️ Your request has been flagged for policy violations. "
               "Please rephrase with a legitimate education question.")

    return {
        "agent_response": msg,
        "messages": state.get("messages", []) + [AIMessage(content=msg)],
        "processing_metadata": {
            **state.get("processing_metadata", {}),
            "agent_used": "rejection_handler",
            "exit_timestamp": datetime.now().isoformat()
        }
    }


# ═════════════════════════════════════════════════════════════════
# NODE 3 — intent_classifier
# ═════════════════════════════════════════════════════════════════

COURSE_KEYWORDS = [
    "course", "class", "prerequisite", "prereq", "enroll", "enrollment",
    "curriculum", "module", "syllabus", "instructor", "professor",
    "lecture", "lesson", "schedule", "semester", "credit", "degree",
    "certificate", "program", "major", "minor", "cs101", "ml201",
    "web301", "data401", "learning path", "difficulty", "duration"
]

SUPPORT_KEYWORDS = [
    "bug", "error", "crash", "broken", "not working", "can't access",
    "issue", "problem", "help", "support", "ticket", "fix", "report",
    "glitch", "loading", "frozen", "slow", "login issue", "locked out",
    "technical", "escalate", "complaint"
]

FAQ_KEYWORDS = [
    "how do i", "how to", "what is", "where can", "faq", "password",
    "reset", "refund", "policy", "payment", "account", "subscription",
    "cancel", "certificate", "download", "access", "pricing"
]


def intent_classifier(state: LearnBotState) -> dict:
    """
    Classify user intent using keyword matching.
    Falls back to 'faq' for ambiguous queries.
    """
    text = state["user_input"].lower()

    scores = {"course": 0, "support": 0, "faq": 0}

    for kw in COURSE_KEYWORDS:
        if kw in text:
            scores["course"] += 1

    for kw in SUPPORT_KEYWORDS:
        if kw in text:
            scores["support"] += 1

    for kw in FAQ_KEYWORDS:
        if kw in text:
            scores["faq"] += 1

    # Default to FAQ for ambiguous queries
    intent = max(scores, key=scores.get) if max(scores.values()) > 0 else "faq"

    return {
        "intent": intent,
        "processing_metadata": {
            **state.get("processing_metadata", {}),
            "intent_scores": scores
        }
    }


def intent_router(state: LearnBotState) -> str:
    """3-way routing based on classified intent."""
    intent = state.get("intent", "faq")
    if intent == "course":
        return "course_handler"
    elif intent == "support":
        return "support_handler"
    return "faq_handler"


# ═════════════════════════════════════════════════════════════════
# NODES 4-6 — Handler Nodes
# ═════════════════════════════════════════════════════════════════

# Groq + Llama 3.x intermittently fails tool calls with `tool_use_failed:
# Failed to call a function`. Retry once on a fresh agent instance — the
# next sample from the model usually emits a valid call.
_GROQ_TOOL_RETRY_MARKERS = ("tool_use_failed", "Failed to call a function")


async def _ainvoke_with_retry(agent_factory, user_input: str, attempts: int = 2):
    last_err = None
    for _ in range(attempts):
        try:
            return await agent_factory().ainvoke({"input": user_input})
        except Exception as e:
            last_err = e
            if not any(m in str(e) for m in _GROQ_TOOL_RETRY_MARKERS):
                raise
    raise last_err


async def course_handler(state: LearnBotState) -> dict:
    """Invoke course_agent for course-related queries."""
    try:
        result = await _ainvoke_with_retry(get_course_agent, state["user_input"])
        response = result.get("output", "I couldn't process your course query.")
        tool_calls = [
            step[0].tool for step in result.get("intermediate_steps", [])
        ]
    except Exception as e:
        response = f"I encountered an issue with the course lookup. Error: {str(e)}"
        tool_calls = []

    return {
        "agent_response": response,
        "tool_calls_made": tool_calls,
        "messages": state.get("messages", []) + [AIMessage(content=response)],
        "processing_metadata": {
            **state.get("processing_metadata", {}),
            "agent_used": "course_agent",
            "exit_timestamp": datetime.now().isoformat()
        }
    }


async def support_handler(state: LearnBotState) -> dict:
    """Invoke support_agent for support-related queries."""
    try:
        result = await _ainvoke_with_retry(get_support_agent, state["user_input"])
        response = result.get("output", "I couldn't process your support request.")
        tool_calls = [
            step[0].tool for step in result.get("intermediate_steps", [])
        ]
    except Exception as e:
        response = f"I encountered an issue with support. Error: {str(e)}"
        tool_calls = []

    return {
        "agent_response": response,
        "tool_calls_made": tool_calls,
        "messages": state.get("messages", []) + [AIMessage(content=response)],
        "processing_metadata": {
            **state.get("processing_metadata", {}),
            "agent_used": "support_agent",
            "exit_timestamp": datetime.now().isoformat()
        }
    }


async def faq_handler(state: LearnBotState) -> dict:
    """Invoke faq_agent for general FAQ queries."""
    try:
        result = await _ainvoke_with_retry(get_faq_agent, state["user_input"])
        response = result.get("output", "I couldn't find an FAQ answer.")
        tool_calls = [
            step[0].tool for step in result.get("intermediate_steps", [])
        ]
    except Exception as e:
        response = f"I encountered an issue with the FAQ lookup. Error: {str(e)}"
        tool_calls = []

    return {
        "agent_response": response,
        "tool_calls_made": tool_calls,
        "messages": state.get("messages", []) + [AIMessage(content=response)],
        "processing_metadata": {
            **state.get("processing_metadata", {}),
            "agent_used": "faq_agent",
            "exit_timestamp": datetime.now().isoformat()
        }
    }


# ═════════════════════════════════════════════════════════════════
# D.4 / D.5 — GRAPH ASSEMBLY & COMPILATION
# ═════════════════════════════════════════════════════════════════

# REFLECTION: How would you add memory/persistence across sessions?
#
# LangGraph supports checkpointers (SqliteSaver, PostgresSaver) that
# serialize state after each node. To add session memory:
#   1. Use a MemorySaver or database-backed checkpointer
#   2. Pass a thread_id with each invocation to track sessions
#   3. The messages list (append-only) naturally accumulates history
#   4. For cross-session memory, use a persistent store (Redis/Postgres)
#      keyed by student_id, storing past intents, resolved tickets, and
#      course interests to personalize future interactions.
# LangGraph's `interrupt_before` / `interrupt_after` can also pause
# the workflow for human approval on HIGH-severity flags.

def build_learnbot_graph():
    """
    Build and compile the LearnBot StateGraph.

    Graph architecture:
      receive_input → safety_check →[conditional]→ intent_classifier → [conditional]→ handler → END
                                    └→ rejection_handler → END
    """
    graph = StateGraph(LearnBotState)

    # Add all 6 nodes + rejection handler
    graph.add_node("receive_input", receive_input)
    graph.add_node("safety_check", safety_check)
    graph.add_node("rejection_handler", rejection_handler)
    graph.add_node("intent_classifier", intent_classifier)
    graph.add_node("course_handler", course_handler)
    graph.add_node("support_handler", support_handler)
    graph.add_node("faq_handler", faq_handler)

    # Entry point
    graph.set_entry_point("receive_input")

    # Edges: receive_input → safety_check
    graph.add_edge("receive_input", "safety_check")

    # Conditional Edge 1: safety → intent or rejection
    graph.add_conditional_edges(
        "safety_check",
        safety_router,
        {
            "intent_classifier": "intent_classifier",
            "rejection_handler": "rejection_handler"
        }
    )

    # rejection_handler → END
    graph.add_edge("rejection_handler", END)

    # Conditional Edge 2: intent → course | support | faq
    graph.add_conditional_edges(
        "intent_classifier",
        intent_router,
        {
            "course_handler": "course_handler",
            "support_handler": "support_handler",
            "faq_handler": "faq_handler"
        }
    )

    # All handlers → END
    graph.add_edge("course_handler", END)
    graph.add_edge("support_handler", END)
    graph.add_edge("faq_handler", END)

    # Compile
    compiled = graph.compile()
    return compiled


# Build the graph at module level for import
learnbot_graph = build_learnbot_graph()


async def run_learnbot(user_input: str) -> dict:
    """
    Execute the full LearnBot workflow for a given user input.

    Args:
        user_input: The student's message.

    Returns:
        Final state dict with all 8 fields populated.
    """
    initial_state: LearnBotState = {
        "messages": [],
        "user_input": user_input,
        "intent": None,
        "safety_status": "pending",
        "safety_flags": [],
        "agent_response": None,
        "tool_calls_made": [],
        "processing_metadata": {}
    }

    result = await learnbot_graph.ainvoke(initial_state)
    return result
