---
name: coding-agents-prompting-flow
description: "Reusable workflow for prompt authoring/adaptation with thin orchestration and explicit HITL approvals. discover -> extract+intake -> blueprint -> for_each_prompt_loop(draft -> hardening -> edit) -> simulate -> validate."
baseSchema: docs/schemas/workflow.md
---

<coding_agents_prompting_flow>

<description>
Rosetta workflow `coding-agents-prompting-flow`. Executes the centralized KB workflow definition.
</description>

<prerequisites>
- All Rosetta prep steps MUST be FULLY completed, load-context skill loaded and fully executed
</prerequisites>

<instructions>
MUST ACQUIRE `workflows/coding-agents-prompting-flow.md` FROM KB and FULLY EXECUTE EXACTLY, ALL PHASES AND STEPS, USING SUBAGENTS AS DEFINED
</instructions>

</coding_agents_prompting_flow>
