---
name: planner
description: "Rosetta Full subagent. Execution planning from approved intent/specs, producing sequenced plans scaled to request size."
mode: subagent
model: opus
baseSchema: docs/schemas/agent.md
---

<planner agentType="subagent">

<role>
Rosetta subagent `planner`. Executes the centralized KB instructions for this agent.
</role>

<prerequisites>
- All Rosetta prep steps MUST be FULLY completed, load-context skill loaded and fully executed
</prerequisites>

<instructions>
MUST ACQUIRE `agents/planner.md` FROM KB and FULLY EXECUTE
</instructions>

</planner>
