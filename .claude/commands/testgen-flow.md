---
name: testgen-flow
description: "MUST apply when test case generation task is assigned. (e.g if a user asks to generate test cases for TICKET-123, create test scenarios from Jira, analyze requirements and generate tests, export tests to TestRail)"
baseSchema: docs/schemas/workflow.md
---

<testgen_flow>

<description>
Rosetta workflow `testgen-flow`. Executes the centralized KB workflow definition.
</description>

<prerequisites>
- All Rosetta prep steps MUST be FULLY completed, load-context skill loaded and fully executed
</prerequisites>

<instructions>
MUST ACQUIRE `workflows/testgen-flow.md` FROM KB and FULLY EXECUTE EXACTLY, ALL PHASES AND STEPS, USING SUBAGENTS AS DEFINED
</instructions>

</testgen_flow>
