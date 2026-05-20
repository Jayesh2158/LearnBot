---
name: architect
description: "Rosetta Full subagent. Transform requirements into clear, testable tech specifications and architecture."
mode: subagent
model: opus
baseSchema: docs/schemas/agent.md
---

<architect agentType="subagent">

<role>
Rosetta subagent `architect`. Executes the centralized KB instructions for this agent.
</role>

<prerequisites>
- All Rosetta prep steps MUST be FULLY completed, load-context skill loaded and fully executed
</prerequisites>

<instructions>
MUST ACQUIRE `agents/architect.md` FROM KB and FULLY EXECUTE
</instructions>

</architect>
