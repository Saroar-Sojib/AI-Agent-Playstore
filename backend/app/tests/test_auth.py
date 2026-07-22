"""Auth flow: signup, login, and per-agent login isolation.

Isolation is the core auth requirement for AgentHub: a user account created
under one agent must not authenticate under a different agent, even with the
same email + password.
"""


def test_signup_then_login_succeeds(client, make_agent):
    make_agent("dentist", profession="Dentist")

    signup = client.post(
        "/api/v1/auth/signup",
        json={"agent_slug": "dentist", "email": "a@example.com", "password": "Passw0rd!"},
    )
    assert signup.status_code == 201
    assert "access_token" in signup.json()

    login = client.post(
        "/api/v1/auth/login",
        json={"agent_slug": "dentist", "email": "a@example.com", "password": "Passw0rd!"},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()


def test_duplicate_signup_under_same_agent_conflicts(client, make_agent):
    make_agent("vet", profession="Veterinarian")
    payload = {"agent_slug": "vet", "email": "b@example.com", "password": "Passw0rd!"}

    first = client.post("/api/v1/auth/signup", json=payload)
    assert first.status_code == 201

    second = client.post("/api/v1/auth/signup", json=payload)
    assert second.status_code == 409


def test_login_is_isolated_per_agent(client, make_agent):
    make_agent("lawyer", profession="Lawyer")
    make_agent("teacher", profession="Teacher")

    client.post(
        "/api/v1/auth/signup",
        json={"agent_slug": "lawyer", "email": "c@example.com", "password": "Passw0rd!"},
    )

    # Correct agent -> succeeds.
    ok = client.post(
        "/api/v1/auth/login",
        json={"agent_slug": "lawyer", "email": "c@example.com", "password": "Passw0rd!"},
    )
    assert ok.status_code == 200

    # Same email, wrong agent -> must fail. The account is scoped to "lawyer"
    # and does not exist under "teacher".
    wrong_agent = client.post(
        "/api/v1/auth/login",
        json={"agent_slug": "teacher", "email": "c@example.com", "password": "Passw0rd!"},
    )
    assert wrong_agent.status_code == 401

    # The same email CAN independently sign up under a second agent — the
    # uniqueness boundary is (agent_id, email), not email alone.
    second_signup = client.post(
        "/api/v1/auth/signup",
        json={"agent_slug": "teacher", "email": "c@example.com", "password": "Passw0rd!"},
    )
    assert second_signup.status_code == 201


def test_wrong_password_rejected(client, make_agent):
    make_agent("chef", profession="Chef")
    client.post(
        "/api/v1/auth/signup",
        json={"agent_slug": "chef", "email": "d@example.com", "password": "Correct123!"},
    )

    bad_login = client.post(
        "/api/v1/auth/login",
        json={"agent_slug": "chef", "email": "d@example.com", "password": "Wrong123!"},
    )
    assert bad_login.status_code == 401


def test_login_unknown_agent_slug_404s(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"agent_slug": "does-not-exist", "email": "x@example.com", "password": "whatever"},
    )
    assert resp.status_code == 404
