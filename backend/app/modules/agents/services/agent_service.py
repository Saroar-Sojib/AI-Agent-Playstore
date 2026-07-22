from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agents.repositories.agent_repository import AgentRepository
from app.modules.agents.schemas.agent_schema import AgentResponse


class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AgentRepository(db)

    async def get_by_slug(self, slug: str) -> AgentResponse:
        agent = await self.repo.get_by_slug(slug)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found"
            )
        return AgentResponse.model_validate(agent)

    async def list_agents(self, page: int = 1, page_size: int = 50) -> dict:
        skip = (page - 1) * page_size
        agents = await self.repo.get_list(skip=skip, limit=page_size)
        total = await self.repo.get_total_count()
        return {
            "data": [AgentResponse.model_validate(a) for a in agents],
            "pagination": {"page": page, "page_size": page_size, "total": total},
        }
