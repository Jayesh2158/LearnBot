---
name: hitl
description: "Rosetta CRITICAL MUST skill to load as Prep Step 3 Step 2 — immediately after orchestrator-contract, right before loading any workflow. Loads the session-wide approval-gate protocol governing when to stop and wait vs proceed. WITHOUT IT decisions proceed silently, violating enterprise policy. Activate it for ALL tasks always — planning, execution, validation, review — regardless of auto-mode, no approval policy, full access. THE ONLY exception: user DIRECTLY EXPLICITLY requests with EXACTLY `fully autonomous` or `No HITL`. Without explicit opt-out this skill is MANDATORY. Do not assume approval from a question or partial response. Contains human-in-the-loop collaboration, questioning, approvals, and user coordination requirements."
tags: []
baseSchema: docs/schemas/skill.md
---

<hitl>

<role>
Rosetta skill `hitl`. Executes the centralized KB instructions for this skill.
</role>

<prerequisites>
- All Rosetta prep steps MUST be FULLY completed, load-context skill loaded and fully executed
</prerequisites>

<instructions>
MUST ACQUIRE `skills/hitl/SKILL.md` FROM KB and FULLY EXECUTE
</instructions>

</hitl>
