from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agents.models.agent import Agent


class AgentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, agent_id: int) -> Optional[Agent]:
        result = await self.db.execute(select(Agent).where(Agent.id == agent_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Agent]:
        result = await self.db.execute(select(Agent).where(Agent.slug == slug))
        return result.scalar_one_or_none()

    async def get_list(self, skip: int = 0, limit: int = 50) -> list[Agent]:
        result = await self.db.execute(
            select(Agent).order_by(Agent.id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_total_count(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(Agent))
        return result.scalar() or 0
