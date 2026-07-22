"""Chat/config resolution logic — pure unit tests, no DB or network.

``_resolve_system_prompt`` is what makes "agent #101 is a config row, not a
code change" true: given an Agent (and optionally a SubAgent), it must pick
the right persona text, and different sub-agents under the same agent must
resolve to demonstrably different prompts (this is what lets 2-5 sub-agents
share one chat UI but behave differently).
"""
from types import SimpleNamespace

from app.modules.chat.services.chat_service import _resolve_system_prompt


def _agent(system_prompt=None, profession="Financial Controller"):
    return SimpleNamespace(system_prompt=system_prompt, profession=profession)


def _sub_agent(system_prompt=None, name="Reconciliation Agent", task_description="Reconcile accounts"):
    return SimpleNamespace(
        system_prompt=system_prompt, name=name, task_description=task_description
    )


def test_uses_agent_system_prompt_when_no_sub_agent():
    agent = _agent(system_prompt="AGENT PROMPT")
    assert _resolve_system_prompt(agent, None) == "AGENT PROMPT"


def test_uses_sub_agent_system_prompt_over_agent_prompt():
    agent = _agent(system_prompt="AGENT PROMPT")
    sub = _sub_agent(system_prompt="SUB PROMPT")
    assert _resolve_system_prompt(agent, sub) == "SUB PROMPT"


def test_different_sub_agents_resolve_to_different_prompts():
    agent = _agent(system_prompt="AGENT PROMPT")
    reconciliation = _sub_agent(name="Reconciliation Agent", system_prompt="Focus on reconciliation.")
    excel = _sub_agent(name="Excel Agent", system_prompt="Focus on spreadsheets.")
    assert _resolve_system_prompt(agent, reconciliation) != _resolve_system_prompt(agent, excel)


def test_falls_back_to_generic_default_when_agent_prompt_missing():
    agent = _agent(system_prompt=None, profession="Teacher")
    prompt = _resolve_system_prompt(agent, None)
    assert "Teacher" in prompt


def test_sub_agent_falls_back_using_its_own_name_and_task():
    agent = _agent(system_prompt="irrelevant here", profession="Financial Controller")
    sub = _sub_agent(system_prompt=None, name="Excel Agent", task_description="Build spreadsheets")
    prompt = _resolve_system_prompt(agent, sub)
    assert "Excel Agent" in prompt
    assert "Build spreadsheets" in prompt
