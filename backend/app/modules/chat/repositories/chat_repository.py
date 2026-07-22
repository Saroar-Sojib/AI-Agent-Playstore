from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agents.models.sub_agent import SubAgent
from app.modules.chat.models.chat_message import ChatMessage
from app.modules.chat.models.conversation import Conversation
from app.modules.chat.models.usage_log import UsageLog


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # -- SubAgent -----------------------------------------------------------

    async def get_sub_agent(self, sub_agent_id: int, agent_id: int) -> Optional[SubAgent]:
        result = await self.db.execute(
            select(SubAgent).where(
                SubAgent.id == sub_agent_id, SubAgent.agent_id == agent_id
            )
        )
        return result.scalar_one_or_none()

    async def list_sub_agents(self, agent_id: int) -> list[SubAgent]:
        result = await self.db.execute(
            select(SubAgent)
            .where(SubAgent.agent_id == agent_id)
            .order_by(SubAgent.order_index)
        )
        return list(result.scalars().all())

    # -- Conversation ---------------------------------------------------------

    async def get_conversation(
        self, conversation_id: int, user_id: int, agent_id: int, sub_agent_id: Optional[int]
    ) -> Optional[Conversation]:
        result = await self.db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id,
                Conversation.agent_id == agent_id,
                Conversation.sub_agent_id == sub_agent_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_conversation_for_user(
        self, conversation_id: int, user_id: int
    ) -> Optional[Conversation]:
        result = await self.db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id, Conversation.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def create_conversation(
        self,
        user_id: int,
        agent_id: int,
        sub_agent_id: Optional[int],
        title: Optional[str] = None,
    ) -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            agent_id=agent_id,
            sub_agent_id=sub_agent_id,
            title=title,
        )
        self.db.add(conversation)
        await self.db.flush()
        return conversation

    # -- ChatMessage ----------------------------------------------------------

    async def get_messages(self, conversation_id: int) -> list[ChatMessage]:
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.id)
        )
        return list(result.scalars().all())

    async def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        token_count: Optional[int] = None,
    ) -> ChatMessage:
        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            token_count=token_count,
        )
        self.db.add(message)
        await self.db.flush()
        return message

    # -- UsageLog ---------------------------------------------------------------

    async def add_usage_log(
        self,
        user_id: Optional[int],
        agent_id: Optional[int],
        sub_agent_id: Optional[int],
        status: str,
        tokens_used: Optional[int] = None,
        latency_ms: Optional[int] = None,
    ) -> UsageLog:
        log = UsageLog(
            user_id=user_id,
            agent_id=agent_id,
            sub_agent_id=sub_agent_id,
            status=status,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
        )
        self.db.add(log)
        await self.db.flush()
        return log
