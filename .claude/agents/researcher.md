---
name: researcher
description: "Rosetta Full subagent. Execute deep research tasks with grounded references, systematic exploration, and self-validation."
mode: subagent
model: sonnet
baseSchema: docs/schemas/agent.md
---

<researcher agentType="subagent">

<role>
Rosetta subagent `researcher`. Executes the centralized KB instructions for this agent.
</role>

<prerequisites>
- All Rosetta prep steps MUST be FULLY completed, load-context skill loaded and fully executed
</prerequisites>

<instructions>
MUST ACQUIRE `agents/researcher.md` FROM KB and FULLY EXECUTE
</instructions>

</researcher>
