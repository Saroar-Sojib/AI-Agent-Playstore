from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.core.rate_limit import RateLimit
from app.infrastructure.database import get_db
from app.modules.agents.models.agent import Agent
from app.modules.agents.repositories.agent_repository import AgentRepository
from app.modules.chat.repositories.chat_repository import ChatRepository
from app.modules.chat.schemas.chat_schemas import (
    ChatMessageResponse,
    ChatRequest,
    ChatResponse,
    SubAgentResponse,
)
from app.modules.chat.services.chat_service import ChatService
from app.modules.users.models.user import User

router = APIRouter()


async def _get_agent_or_404(slug: str, db: AsyncSession) -> Agent:
    agent = await AgentRepository(db).get_by_slug(slug)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent '{slug}' not found")
    return agent


def _enforce_agent_scope(user: User, agent: Agent) -> None:
    """A user provisioned under agent A cannot chat as agent B."""
    if user.agent_id != agent.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is not scoped to this agent",
        )


@router.get("/{slug}/sub-agents", response_model=list[SubAgentResponse])
async def list_sub_agents(slug: str, db: AsyncSession = Depends(get_db)):
    """Public catalog listing of an agent's sub-agents, ordered for display."""
    agent = await _get_agent_or_404(slug, db)
    sub_agents = await ChatRepository(db).list_sub_agents(agent.id)
    return sub_agents


@router.post(
    "/{slug}/chat",
    response_model=ChatResponse,
    dependencies=[Depends(RateLimit("chat.agent", max_requests=20, window_seconds=60))],
)
async def chat_with_agent(
    slug: str,
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Chat directly with the main agent persona."""
    agent = await _get_agent_or_404(slug, db)
    _enforce_agent_scope(current_user, agent)

    conversation_id, reply = await ChatService(db).send_message(
        user=current_user,
        agent=agent,
        sub_agent=None,
        conversation_id=payload.conversation_id,
        user_message=payload.message,
    )
    return ChatResponse(conversation_id=conversation_id, reply=reply)


@router.post(
    "/{slug}/sub-agents/{sub_agent_id}/chat",
    response_model=ChatResponse,
    dependencies=[Depends(RateLimit("chat.sub_agent", max_requests=20, window_seconds=60))],
)
async def chat_with_sub_agent(
    slug: str,
    sub_agent_id: int,
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Chat with one specific sub-agent belonging to this agent."""
    agent = await _get_agent_or_404(slug, db)
    _enforce_agent_scope(current_user, agent)

    repo = ChatRepository(db)
    sub_agent = await repo.get_sub_agent(sub_agent_id, agent.id)
    if sub_agent is None:
        raise HTTPException(status_code=404, detail="Sub-agent not found")

    conversation_id, reply = await ChatService(db).send_message(
        user=current_user,
        agent=agent,
        sub_agent=sub_agent,
        conversation_id=payload.conversation_id,
        user_message=payload.message,
    )
    return ChatResponse(conversation_id=conversation_id, reply=reply)


@router.get(
    "/{slug}/conversations/{conversation_id}/messages",
    response_model=list[ChatMessageResponse],
)
async def get_conversation_messages(
    slug: str,
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reload a conversation's message history — must belong to the caller."""
    agent = await _get_agent_or_404(slug, db)
    _enforce_agent_scope(current_user, agent)

    repo = ChatRepository(db)
    conversation = await repo.get_conversation_for_user(conversation_id, current_user.id)
    if conversation is None or conversation.agent_id != agent.id:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return await repo.get_messages(conversation_id)
