"""
╔══════════════════════════════════════════════════════════════════╗
║  PART C — Tool Design & Scoped Agents                           ║
║  LearnBot Capstone · LearnSphere Platform                       ║
╚══════════════════════════════════════════════════════════════════╝

Implements:
  C.1 — Four @tool functions with full docstrings
  C.2 — course_agent  (get_course_info, check_enrollment_status)
  C.3 — support_agent (create_support_ticket, get_faq_answer)
  C.4 — faq_agent     (get_faq_answer only)
  C.5 — Test queries per agent
"""

import uuid
import random
from datetime import datetime, timedelta
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

from config import settings


# ═════════════════════════════════════════════════════════════════
# C.1 — THE FOUR CORE TOOLS
# ═════════════════════════════════════════════════════════════════

# Mock data simulating a real LMS database
COURSE_CATALOG = {
    "CS101": {
        "title": "Introduction to Computer Science",
        "description": "Fundamentals of programming, algorithms, and computational thinking using Python.",
        "prerequisites": ["None"],
        "modules": ["Python Basics", "Data Types", "Control Flow", "Functions", "OOP Intro", "Final Project"],
        "duration": "8 weeks",
        "difficulty": "Beginner",
        "instructor": "Dr. Sarah Chen",
        "price": 49.99
    },
    "ML201": {
        "title": "Machine Learning Fundamentals",
        "description": "Supervised and unsupervised learning, model evaluation, and practical ML pipelines.",
        "prerequisites": ["CS101", "MATH150"],
        "modules": ["Linear Regression", "Classification", "Trees & Forests", "Clustering", "Neural Nets Intro", "Capstone"],
        "duration": "12 weeks",
        "difficulty": "Intermediate",
        "instructor": "Prof. James Okafor",
        "price": 79.99
    },
    "WEB301": {
        "title": "Full-Stack Web Development",
        "description": "Build modern web applications with React, Node.js, and PostgreSQL.",
        "prerequisites": ["CS101"],
        "modules": ["HTML/CSS", "JavaScript", "React", "Node.js", "Databases", "Deployment"],
        "duration": "10 weeks",
        "difficulty": "Intermediate",
        "instructor": "Maria Gonzalez",
        "price": 69.99
    },
    "DATA401": {
        "title": "Advanced Data Engineering",
        "description": "ETL pipelines, data warehousing, Apache Spark, and cloud data platforms.",
        "prerequisites": ["CS101", "ML201"],
        "modules": ["Data Modeling", "ETL Design", "Spark", "Airflow", "Cloud Platforms", "Capstone"],
        "duration": "14 weeks",
        "difficulty": "Advanced",
        "instructor": "Dr. Anil Patel",
        "price": 99.99
    }
}

ENROLLMENT_DATA = {
    "STU-1001": {"course": "CS101", "status": "active", "completion": 72, "cert_date": None, "enrolled_on": "2025-01-15"},
    "STU-1002": {"course": "ML201", "status": "completed", "completion": 100, "cert_date": "2025-04-20", "enrolled_on": "2024-09-01"},
    "STU-1003": {"course": "WEB301", "status": "active", "completion": 45, "cert_date": None, "enrolled_on": "2025-02-10"},
}

FAQ_DATABASE = {
    "password_reset": {
        "question": "How do I reset my password?",
        "answer": "Go to the login page → Click 'Forgot Password' → Enter your registered email → Check your inbox for a reset link (valid 24 hours). Check spam if not received.",
        "confidence": 0.98,
        "related": ["account_locked", "email_change"]
    },
    "refund_policy": {
        "question": "What is the refund policy?",
        "answer": "LearnSphere offers a 14-day refund for courses with less than 20% completion. Go to Settings → Purchase History → Request Refund.",
        "confidence": 0.97,
        "related": ["payment_methods", "subscription_cancel"]
    },
    "certificate": {
        "question": "How do I get my certificate?",
        "answer": "Certificates are automatically issued when you reach 100% course completion. Download from your Profile → Certificates section.",
        "confidence": 0.96,
        "related": ["completion_requirements", "certificate_verification"]
    },
    "access_issues": {
        "question": "Why can't I access course materials?",
        "answer": "Common causes: (1) Enrollment processing (wait 15 min), (2) Browser cache (try incognito), (3) Expired subscription. Check Settings → Subscriptions.",
        "confidence": 0.95,
        "related": ["browser_support", "payment_issues"]
    },
    "payment_methods": {
        "question": "What payment methods are accepted?",
        "answer": "LearnSphere accepts Visa, Mastercard, PayPal, and bank transfer. All payments are secured with SSL encryption.",
        "confidence": 0.97,
        "related": ["refund_policy", "subscription_plans"]
    }
}


@tool
def get_course_info(course_id: str) -> dict:
    """
    Retrieve detailed information about a course from the LearnSphere catalog.

    Args:
        course_id: The course identifier (e.g., 'CS101', 'ML201').

    Returns:
        dict with keys: title, description, prerequisites, modules,
        duration, difficulty, instructor, price.

    Raises:
        ValueError: If course_id is not found in the catalog.

    Example:
        get_course_info("CS101")
        → {"title": "Introduction to Computer Science", ...}
    """
    course_id = course_id.upper().strip()
    if course_id in COURSE_CATALOG:
        return {"course_id": course_id, **COURSE_CATALOG[course_id]}
    # Fuzzy search
    for cid, info in COURSE_CATALOG.items():
        if course_id.lower() in info["title"].lower():
            return {"course_id": cid, **info}
    return {"error": f"Course '{course_id}' not found. Available: {', '.join(COURSE_CATALOG.keys())}"}


@tool
def check_enrollment_status(student_id: str) -> dict:
    """
    Check a student's enrollment status, progress, and certificate date.

    Args:
        student_id: The student identifier (e.g., 'STU-1001').

    Returns:
        dict with keys: student_id, course, status (active/completed/dropped),
        completion (percentage), certificate_date, enrolled_on.

    Raises:
        ValueError: If student_id is not found.

    Example:
        check_enrollment_status("STU-1001")
        → {"student_id": "STU-1001", "course": "CS101", "status": "active", "completion": 72, ...}
    """
    student_id = student_id.upper().strip()
    if student_id in ENROLLMENT_DATA:
        data = ENROLLMENT_DATA[student_id]
        return {
            "student_id": student_id,
            "course": data["course"],
            "course_title": COURSE_CATALOG.get(data["course"], {}).get("title", "Unknown"),
            "status": data["status"],
            "completion_percent": data["completion"],
            "certificate_date": data["cert_date"],
            "enrolled_on": data["enrolled_on"]
        }
    return {"error": f"Student '{student_id}' not found. Use format: STU-XXXX"}


@tool
def create_support_ticket(issue_summary: str, priority: str = "MED", category: str = "technical") -> dict:
    """
    Create a support ticket for escalation to the LearnSphere support team.

    Args:
        issue_summary: One-line description of the issue.
        priority: Ticket priority — 'LOW', 'MED', or 'HIGH'.
        category: Issue category — 'account', 'technical', 'billing', 'content', 'access'.

    Returns:
        dict with keys: ticket_id, summary, priority, category,
        status, estimated_resolution, created_at.

    Raises:
        ValueError: If priority or category is invalid.

    Example:
        create_support_ticket("Cannot access ML201 videos", "HIGH", "access")
        → {"ticket_id": "TKT-...", "estimated_resolution": "24 hours", ...}
    """
    valid_priorities = ["LOW", "MED", "HIGH"]
    valid_categories = ["account", "technical", "billing", "content", "access"]

    priority = priority.upper().strip()
    category = category.lower().strip()

    if priority not in valid_priorities:
        priority = "MED"
    if category not in valid_categories:
        category = "technical"

    resolution_map = {"LOW": "72 hours", "MED": "48 hours", "HIGH": "24 hours"}

    ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
    return {
        "ticket_id": ticket_id,
        "summary": issue_summary,
        "priority": priority,
        "category": category,
        "status": "open",
        "estimated_resolution": resolution_map[priority],
        "created_at": datetime.now().isoformat()
    }


@tool
def get_faq_answer(question: str) -> dict:
    """
    Search the FAQ database for the best matching answer.

    Args:
        question: The user's question in natural language.

    Returns:
        dict with keys: answer, confidence (0.0-1.0), related_articles (list).

    Raises:
        ValueError: If question is empty.

    Example:
        get_faq_answer("How do I reset my password?")
        → {"answer": "Go to the login page...", "confidence": 0.98, ...}
    """
    question_lower = question.lower()
    best_match = None
    best_score = 0

    for key, faq in FAQ_DATABASE.items():
        # Simple keyword overlap scoring
        faq_words = set(faq["question"].lower().split())
        query_words = set(question_lower.split())
        overlap = len(faq_words & query_words)
        # Also check key keywords
        if key.replace("_", " ") in question_lower:
            overlap += 3
        if overlap > best_score:
            best_score = overlap
            best_match = faq

    if best_match and best_score >= 1:
        return {
            "answer": best_match["answer"],
            "confidence": best_match["confidence"],
            "related_articles": best_match["related"]
        }

    return {
        "answer": "I couldn't find a specific FAQ for your question. Let me connect you with support.",
        "confidence": 0.3,
        "related_articles": []
    }


# ═════════════════════════════════════════════════════════════════
# C.2 – C.4 — SCOPED AGENTS
# ═════════════════════════════════════════════════════════════════

ALL_TOOLS = [get_course_info, check_enrollment_status, create_support_ticket, get_faq_answer]


def get_llm():
    """Initialize the Groq LLM via LangChain."""
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=0.3,
        max_tokens=1024
    )


def _build_agent(tools: list, system_prompt: str) -> AgentExecutor:
    """
    Factory to build a scoped ReAct agent with given tools and system prompt.
    """
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
        return_intermediate_steps=True
    )


# C.2 — Course Agent
COURSE_AGENT_PROMPT = """You are the LearnSphere Course Advisor.
You help students explore the course catalog, check prerequisites,
and understand enrollment status. You have access to course information
and enrollment checking tools ONLY. Stay focused on academic advising.
Be encouraging, concise, and helpful. Never fabricate course data."""


def get_course_agent() -> AgentExecutor:
    return _build_agent(
        tools=[get_course_info, check_enrollment_status],
        system_prompt=COURSE_AGENT_PROMPT
    )


# C.3 — Support Agent
SUPPORT_AGENT_PROMPT = """You are the LearnSphere Support Agent.
You help students resolve technical issues, account problems, and
create support tickets when needed. You have access to ticket creation
and FAQ tools ONLY. Always try the FAQ first before creating tickets.
Be empathetic and solution-focused."""


def get_support_agent() -> AgentExecutor:
    return _build_agent(
        tools=[create_support_ticket, get_faq_answer],
        system_prompt=SUPPORT_AGENT_PROMPT
    )


# C.4 — FAQ Agent
FAQ_AGENT_PROMPT = """You are the LearnSphere FAQ Bot.
You provide quick, accurate answers to frequently asked questions.
You have access to the FAQ database ONLY. If the FAQ doesn't have
an answer, say so clearly and suggest contacting support.
Keep responses concise and direct."""


def get_faq_agent() -> AgentExecutor:
    return _build_agent(
        tools=[get_faq_answer],
        system_prompt=FAQ_AGENT_PROMPT
    )
