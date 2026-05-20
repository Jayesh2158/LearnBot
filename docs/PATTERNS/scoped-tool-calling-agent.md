# Pattern — Scoped tool-calling agent factory

## What it solves

Each LearnBot intent needs an LLM agent that can only invoke tools relevant to its scope. The factory makes the scoping the security boundary — if an agent doesn't receive a tool, the LLM cannot call it.

## When to use

- Adding a new intent that calls tools — write a new `get_<intent>_agent()` that passes only the allowed tools.
- Changing an existing agent's tool surface — change the `tools=[...]` list in its `get_*_agent()` function.

## Where it occurs

- [tools_agents.py:288](../../tools_agents.py) `_build_agent(tools, system_prompt)` factory.
- [tools_agents.py:317](../../tools_agents.py) `get_course_agent()` — tools `[get_course_info, check_enrollment_status]`.
- [tools_agents.py:332](../../tools_agents.py) `get_support_agent()` — tools `[create_support_ticket, get_faq_answer]`.
- [tools_agents.py:347](../../tools_agents.py) `get_faq_agent()` — tools `[get_faq_answer]`.

## Template

```python
def _build_agent(tools: list, system_prompt: str) -> AgentExecutor:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )

MY_AGENT_PROMPT = """You are the LearnSphere <Role>.
You help with <scope>. You have access to <tool list> ONLY. Stay focused."""

def get_my_agent() -> AgentExecutor:
    return _build_agent(
        tools=[my_tool_a, my_tool_b],
        system_prompt=MY_AGENT_PROMPT,
    )
```

## Extension points

- New agents: add a `get_<name>_agent()` and a `*_AGENT_PROMPT` constant; do not modify `_build_agent`.
- Common config (max_iterations, verbose, handle_parsing_errors): change in `_build_agent` once.

## Pitfalls

- Do not pass tools to an agent that fall outside its scope — the scoping is the security boundary, not just organization.
- Do not bypass the factory by calling `AgentExecutor(...)` directly elsewhere.
