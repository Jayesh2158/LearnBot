---
name: discoverer
description: "Rosetta Lightweight subagent. Gather project context, existing patterns, affected areas, and dependencies."
mode: subagent
model: sonnet
baseSchema: docs/schemas/agent.md
---

<discoverer agentType="subagent">

<role>
Rosetta subagent `discoverer`. Executes the centralized KB instructions for this agent.
</role>

<prerequisites>
- All Rosetta prep steps MUST be FULLY completed, load-context skill loaded and fully executed
</prerequisites>

<instructions>
MUST ACQUIRE `agents/discoverer.md` FROM KB and FULLY EXECUTE
</instructions>

</discoverer>
