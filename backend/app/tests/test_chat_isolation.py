"""Chat endpoint isolation + per-sub-agent specialization.

The LLM call itself is mocked (no network access, no real API key needed in
CI) — what's under test is that (a) a user can't chat as an agent they
weren't provisioned under, and (b) two different sub-agents under the same
agent feed demonstrably different system prompts to the LLM for the exact
same user message, which is the mechanism behind "shared chat UI, different
backend behavior per sub-agent".
"""
import pytest

import app.modules.chat.services.chat_service as chat_service_module


@pytest.fixture
def mock_llm(monkeypatch):
    """Replace the real Gemini call with a stub that records the
    system_prompt it was invoked with, keyed by call order."""
    captured = {"calls": []}

    async def fake_generate_reply(system_prompt, history, user_message):
        captured["calls"].append(system_prompt)
        return f"echo: {user_message}", {"latency_ms": 1, "tokens_used": 5}

    monkeypatch.setattr(chat_service_module, "generate_reply", fake_generate_reply)
    return captured


def _signup(client, agent_slug, email="user@example.com", password="Passw0rd!"):
    resp = client.post(
        "/api/v1/auth/signup",
        json={"agent_slug": agent_slug, "email": email, "password": password},
    )
    return resp.json()["access_token"]


def test_chat_rejects_cross_agent_access(client, make_agent, mock_llm):
    make_agent("doctor", profession="Doctor")
    make_agent("nurse", profession="Nurse")
    token = _signup(client, "doctor")

    resp = client.post(
        "/api/v1/agents/nurse/chat",
        json={"message": "hi"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
    assert mock_llm["calls"] == []  # never reached the LLM


def test_chat_with_own_agent_succeeds(client, make_agent, mock_llm):
    make_agent("architect", profession="Architect", system_prompt="You are an architect.")
    token = _signup(client, "architect")

    resp = client.post(
        "/api/v1/agents/architect/chat",
        json={"message": "hi"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"] == "echo: hi"
    assert mock_llm["calls"] == ["You are an architect."]


def test_different_sub_agents_receive_different_system_prompts(client, make_agent, make_sub_agent, mock_llm):
    agent_id = make_agent("financial-controller-2", profession="Financial Controller")
    recon_id = make_sub_agent(
        agent_id,
        name="Reconciliation Agent",
        system_prompt="Focus ONLY on reconciliation tasks.",
        order_index=1,
    )
    excel_id = make_sub_agent(
        agent_id,
        name="Excel Agent",
        system_prompt="Focus ONLY on spreadsheet tasks.",
        order_index=2,
    )
    token = _signup(client, "financial-controller-2")
    headers = {"Authorization": f"Bearer {token}"}
    same_question = {"message": "What should I look at first?"}

    r1 = client.post(
        f"/api/v1/agents/financial-controller-2/sub-agents/{recon_id}/chat",
        json=same_question,
        headers=headers,
    )
    r2 = client.post(
        f"/api/v1/agents/financial-controller-2/sub-agents/{excel_id}/chat",
        json=same_question,
        headers=headers,
    )

    assert r1.status_code == 200 and r2.status_code == 200
    prompt_recon, prompt_excel = mock_llm["calls"]
    assert prompt_recon != prompt_excel
    assert "reconciliation" in prompt_recon.lower()
    assert "spreadsheet" in prompt_excel.lower()


def test_chat_with_unknown_sub_agent_404s(client, make_agent, mock_llm):
    make_agent("plumber", profession="Plumber")
    token = _signup(client, "plumber")

    resp = client.post(
        "/api/v1/agents/plumber/sub-agents/999999/chat",
        json={"message": "hi"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


def test_chat_without_auth_is_rejected(client, make_agent, mock_llm):
    make_agent("pilot", profession="Pilot")
    resp = client.post("/api/v1/agents/pilot/chat", json={"message": "hi"})
    assert resp.status_code in (401, 403)
