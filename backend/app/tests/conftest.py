"""Shared pytest fixtures.

Tests run against a real (throwaway) Postgres database rather than SQLite —
the app's async engine is asyncpg-specific (pool args, GUC session config in
``get_db``), so a same-dialect test DB avoids subtle behavior gaps. Point
``TEST_DATABASE_URL``/``TEST_DATABASE_URL_ASYNC`` at a scratch database (CI
spins one up as a service container; locally, `docker compose up postgres`
then create an extra `_test` database, or just run against the same instance
with a different db name).

Schema is created directly via ``Base.metadata.create_all`` over a plain sync
engine — deliberately bypassing Alembic here so schema setup has no
event-loop entanglement with the app's async engine.
"""
from __future__ import annotations

import os

os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/ai_agent_playstore_test",
    ),
)
os.environ.setdefault(
    "DATABASE_URL_ASYNC",
    os.environ.get(
        "TEST_DATABASE_URL_ASYNC",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_agent_playstore_test",
    ),
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("LLM_API_KEY", "test-llm-key-unused-because-mocked")
os.environ.setdefault("DEBUG", "True")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.infrastructure.database import Base
from app.modules.agents.models.agent import Agent
from app.modules.agents.models.sub_agent import SubAgent

# Force every model module to import so its Table registers on Base.metadata.
# (Using `from ... import ...` throughout, deliberately never a bare
# `import app.foo.bar` statement here — that form rebinds the local name
# `app` to the top-level package, which would clobber the FastAPI `app`
# instance imported below.)
from app.modules.chat.models import conversation as _conversation_model  # noqa: F401
from app.modules.chat.models import chat_message as _chat_message_model  # noqa: F401
from app.modules.chat.models import usage_log as _usage_log_model  # noqa: F401
from app.modules.users.models import user as _user_model  # noqa: F401
from app.main import app

_sync_engine = create_engine(settings.DATABASE_URL)
_SyncSession = sessionmaker(bind=_sync_engine, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.drop_all(_sync_engine)
    Base.metadata.create_all(_sync_engine)
    yield
    Base.metadata.drop_all(_sync_engine)


@pytest.fixture(autouse=True)
def _clean_tables():
    yield
    with _sync_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture
def client():
    """One TestClient per test, used as a context manager so every request
    in a test shares a single event loop/portal — the app's asyncpg pool is
    loop-bound, so mixing loops across requests raises "attached to a
    different loop". Exiting the ``with`` block runs the app's shutdown
    event (see ``main._dispose_engine``), which disposes the pool from
    *within* that same loop before it closes — so the next test's (new)
    loop never inherits connections from this one.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def make_agent():
    """Insert an Agent row directly (there's no HTTP endpoint to create one —
    that's the content-pipeline script's job); returns the new agent's id."""

    def _make(
        slug: str,
        profession: str = "Test Professional",
        industry: str = "Testing",
        system_prompt: str = "You are a helpful test persona.",
    ) -> int:
        with _SyncSession() as session:
            agent = Agent(
                slug=slug,
                profession=profession,
                industry=industry,
                system_prompt=system_prompt,
            )
            session.add(agent)
            session.commit()
            session.refresh(agent)
            return agent.id

    return _make


@pytest.fixture
def make_sub_agent():
    def _make(
        agent_id: int,
        name: str,
        system_prompt: str,
        task_description: str = "",
        order_index: int = 1,
    ) -> int:
        with _SyncSession() as session:
            sub_agent = SubAgent(
                agent_id=agent_id,
                name=name,
                task_description=task_description,
                system_prompt=system_prompt,
                order_index=order_index,
            )
            session.add(sub_agent)
            session.commit()
            session.refresh(sub_agent)
            return sub_agent.id

    return _make
