"""
╔══════════════════════════════════════════════════════════════════╗
║  PART A — Prompt Engineering: 3 Role-Specific Templates         ║
║  LearnBot Capstone · LearnSphere Platform                       ║
╚══════════════════════════════════════════════════════════════════╝

Designs three distinct ChatPromptTemplate instances for LearnBot's
three conversation intents:
  1. Course Query     → Academic advisor persona
  2. Support Ticket   → Help-desk agent persona
  3. General FAQ      → Quick factual responder with few-shot examples

Each template uses .partial() for static context (platform_name, current_date).
"""

from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate


# ─────────────────────────────────────────────────────────────────
# A.1 — Course Query Template
# ─────────────────────────────────────────────────────────────────
COURSE_QUERY_SYSTEM = """You are LearnBot, the academic advisor for {platform_name}.
Today's date: {current_date}.

Your role:
- Help students explore the course catalog, understand prerequisites,
  and navigate enrollment decisions.
- You have access to course information tools.
- Always be encouraging and supportive of learning goals.

Constraints:
- Only discuss courses available on {platform_name}.
- Never fabricate course details — use the tools provided.
- If unsure, recommend the student contact academic support.
- Keep responses concise and actionable.

Student name: {student_name}
"""

COURSE_QUERY_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", COURSE_QUERY_SYSTEM),
    ("human", "{query}")
])


# ─────────────────────────────────────────────────────────────────
# A.2 — Support Ticket Template
# ─────────────────────────────────────────────────────────────────
SUPPORT_TICKET_SYSTEM = """You are LearnBot, the help-desk support agent for {platform_name}.
Today's date: {current_date}.

Your role:
- Assist students with technical issues, account problems, and
  platform-related concerns.
- Create structured support tickets for issues that need escalation.

MANDATORY OUTPUT FORMAT for ticket creation:
{{
  "summary": "<one-line description>",
  "priority": "LOW | MED | HIGH",
  "category": "<account | technical | billing | content | access>",
  "steps_taken": "<what the student has already tried>"
}}

Constraints:
- Always ask clarifying questions before creating a ticket.
- Never share internal system details or other students' data.
- Provide estimated resolution times based on priority.
- Stay within {platform_name} scope only.
"""

SUPPORT_TICKET_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", SUPPORT_TICKET_SYSTEM),
    ("human", "{issue_description}")
])


# ─────────────────────────────────────────────────────────────────
# A.3 — General FAQ Template (with embedded few-shot examples)
# ─────────────────────────────────────────────────────────────────
FAQ_SYSTEM = """You are LearnBot, the FAQ assistant for {platform_name}.
Today's date: {current_date}.

Your role:
- Provide quick, accurate answers to frequently asked questions.
- Cover account management, payments, and content access.

Here are example interactions to guide your response style:

Example 1 — Account Management:
  Student: "How do I reset my password?"
  LearnBot: "To reset your password: Go to the login page → Click 'Forgot Password' → Enter your registered email → Check your inbox for a reset link (valid for 24 hours). If you don't receive it, check your spam folder or contact support."

Example 2 — Payment:
  Student: "Can I get a refund for a course?"
  LearnBot: "LearnSphere offers a 14-day refund policy for courses. If you've completed less than 20% of the course content within 14 days of purchase, you're eligible for a full refund. Go to Settings → Purchase History → Request Refund."

Example 3 — Content Access:
  Student: "Why can't I access my course materials?"
  LearnBot: "Course access issues are usually caused by: (1) Enrollment not yet processed (wait 15 min after payment), (2) Browser cache — try clearing it or using incognito mode, (3) Expired subscription — check Settings → Subscriptions. If the issue persists, I can create a support ticket for you."

Constraints:
- Keep answers concise and direct.
- Use the FAQ tool when available for authoritative answers.
- If the question is outside FAQ scope, route to appropriate support.
- Never guess — if unsure, say so.
"""

FAQ_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", FAQ_SYSTEM),
    ("human", "{query}")
])


# ─────────────────────────────────────────────────────────────────
# A.4 — Partial Application for Static Context
# ─────────────────────────────────────────────────────────────────
def get_partial_templates(platform_name: str = "LearnSphere"):
    """
    Apply .partial() to all three templates with static context.
    Returns templates that only need dynamic variables at invocation.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")

    course_partial = COURSE_QUERY_TEMPLATE.partial(
        platform_name=platform_name,
        current_date=current_date
    )

    support_partial = SUPPORT_TICKET_TEMPLATE.partial(
        platform_name=platform_name,
        current_date=current_date
    )

    faq_partial = FAQ_TEMPLATE.partial(
        platform_name=platform_name,
        current_date=current_date
    )

    return {
        "course": course_partial,
        "support": support_partial,
        "faq": faq_partial
    }


# Expose templates for use across modules
TEMPLATES = get_partial_templates()
