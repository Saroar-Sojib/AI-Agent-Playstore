from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from app.core.config import settings
from collections.abc import AsyncGenerator

engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            from app.core.user_context import current_agent_id

            agent_id = current_agent_id.get()

            # Bind a session-scoped GUC (third arg = false) so it survives
            # commit/begin cycles within the request. Transaction-scoped
            # (SET LOCAL) GUCs are wiped on commit, which then breaks any
            # SELECT/refresh issued after a commit (RLS filters the row out,
            # if/when an agent-scoped RLS policy is added later). Cleanup in
            # the finally block resets it before the connection returns to
            # the pool — otherwise a recycled connection would leak agent
            # context into the next request.
            if agent_id:
                await session.execute(
                    text("SELECT set_config('app.agent_id', :aid, false)"),
                    {"aid": str(agent_id)},
                )
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            try:
                await session.execute(
                    text("SELECT set_config('app.agent_id', '', false)")
                )
            except Exception:
                pass
