from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db
from app.modules.agents.schemas.agent_schema import AgentResponse
from app.modules.agents.services.agent_service import AgentService

router = APIRouter()


def get_agent_service(db: AsyncSession = Depends(get_db)) -> AgentService:
    return AgentService(db)


@router.get("/", response_model=dict)
async def list_agents(
    page: int = 1,
    page_size: int = 50,
    service: AgentService = Depends(get_agent_service),
):
    """Public catalog listing — every agent persona a user can sign up for."""
    return await service.list_agents(page, page_size)


@router.get("/{slug}", response_model=AgentResponse)
async def get_agent(
    slug: str,
    service: AgentService = Depends(get_agent_service),
):
    """Public catalog detail for a single agent persona."""
    return await service.get_by_slug(slug)
