---
name: executor
description: "Rosetta Lightweight subagent. Run simple commands, collect results, and summarize to prevent parent context overflow."
mode: subagent
model: haiku
baseSchema: docs/schemas/agent.md
---

<executor agentType="subagent">

<role>
Rosetta subagent `executor`. Executes the centralized KB instructions for this agent.
</role>

<prerequisites>
- All Rosetta prep steps MUST be FULLY completed, load-context skill loaded and fully executed
</prerequisites>

<instructions>
MUST ACQUIRE `agents/executor.md` FROM KB and FULLY EXECUTE
</instructions>

</executor>
