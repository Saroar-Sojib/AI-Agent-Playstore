from __future__ import annotations

import logging
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.agents.models.agent import Agent
from app.modules.agents.models.sub_agent import SubAgent
from app.modules.chat.repositories.chat_repository import ChatRepository
from app.modules.chat.services.llm_client import LLMError, generate_reply
from app.modules.users.models.user import User

logger = logging.getLogger(__name__)


def _default_system_prompt(agent: Agent, sub_agent: Optional[SubAgent]) -> str:
    if sub_agent is not None:
        base = f"You are the {sub_agent.name}, a specialized AI assistant for {agent.profession}."
        if sub_agent.task_description:
            base += f" Your task: {sub_agent.task_description}"
        return base
    return f"You are a helpful AI assistant acting as a {agent.profession}."


def _resolve_system_prompt(agent: Agent, sub_agent: Optional[SubAgent]) -> str:
    if sub_agent is not None:
        if sub_agent.system_prompt:
            return sub_agent.system_prompt
        return _default_system_prompt(agent, sub_agent)
    if agent.system_prompt:
        return agent.system_prompt
    return _default_system_prompt(agent, None)


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ChatRepository(db)

    async def send_message(
        self,
        *,
        user: User,
        agent: Agent,
        sub_agent: Optional[SubAgent],
        conversation_id: Optional[int],
        user_message: str,
    ) -> tuple[int, str]:
        sub_agent_id = sub_agent.id if sub_agent is not None else None

        conversation = None
        if conversation_id is not None:
            conversation = await self.repo.get_conversation(
                conversation_id, user.id, agent.id, sub_agent_id
            )
            if conversation is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found",
                )
        else:
            conversation = await self.repo.create_conversation(
                user_id=user.id, agent_id=agent.id, sub_agent_id=sub_agent_id
            )

        history_rows = await self.repo.get_messages(conversation.id)
        history = [{"role": row.role, "content": row.content} for row in history_rows]

        system_prompt = _resolve_system_prompt(agent, sub_agent)

        # Persist the user's turn regardless of what happens with the LLM
        # call, so the conversation history stays complete.
        await self.repo.add_message(conversation.id, role="user", content=user_message)

        try:
            reply_text, metrics = await generate_reply(system_prompt, history, user_message)
        except LLMError as exc:
            logger.warning("LLM call failed for conversation %s: %s", conversation.id, exc)
            await self.repo.add_usage_log(
                user_id=user.id,
                agent_id=agent.id,
                sub_agent_id=sub_agent_id,
                status="error",
            )
            await self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="The AI service is currently unavailable. Please try again.",
            ) from exc

        await self.repo.add_message(
            conversation.id,
            role="assistant",
            content=reply_text,
            token_count=metrics.get("tokens_used"),
        )
        await self.repo.add_usage_log(
            user_id=user.id,
            agent_id=agent.id,
            sub_agent_id=sub_agent_id,
            status="success",
            tokens_used=metrics.get("tokens_used"),
            latency_ms=metrics.get("latency_ms"),
        )
        await self.db.commit()

        return conversation.id, reply_text
