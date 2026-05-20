---
name: engineer
description: "Rosetta Full subagent. Execute implementation and testing tasks with high quality, assuming engineering identity provided by orchestrator."
mode: subagent
model: sonnet
baseSchema: docs/schemas/agent.md
---

<engineer agentType="subagent">

<role>
Rosetta subagent `engineer`. Executes the centralized KB instructions for this agent.
</role>

<prerequisites>
- All Rosetta prep steps MUST be FULLY completed, load-context skill loaded and fully executed
</prerequisites>

<instructions>
MUST ACQUIRE `agents/engineer.md` FROM KB and FULLY EXECUTE
</instructions>

</engineer>
