from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str, agent_id: Optional[int] = None) -> User | None:
        query = select(User).where(User.email == email)
        if agent_id is not None:
            query = query.where(User.agent_id == agent_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        agent_id: int,
        password_hash: str,
    ) -> User:
        user = User(email=email, agent_id=agent_id, password_hash=password_hash)
        self.db.add(user)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def exists_by_email(self, email: str, agent_id: int) -> bool:
        """True if ``(agent_id, email)`` already has a (non-deleted) user."""
        result = await self.db.execute(
            select(User.id).where(
                User.email == email,
                User.agent_id == agent_id,
                User.deleted_at.is_(None),
            )
        )
        return result.first() is not None
