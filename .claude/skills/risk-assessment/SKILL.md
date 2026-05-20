---
name: risk-assessment
description: "Rosetta MUST skill. MUST activate before execution when environment has access to databases, cloud services, S3, or similar external systems. MUST activate when assessing environment risk level. SHOULD be invoked manually before any new environment interaction."
tags: []
baseSchema: docs/schemas/skill.md
---

<risk_assessment>

<role>
Rosetta skill `risk-assessment`. Executes the centralized KB instructions for this skill.
</role>

<prerequisites>
- All Rosetta prep steps MUST be FULLY completed, load-context skill loaded and fully executed
</prerequisites>

<instructions>
MUST ACQUIRE `skills/risk-assessment/SKILL.md` FROM KB and FULLY EXECUTE
</instructions>

</risk_assessment>
