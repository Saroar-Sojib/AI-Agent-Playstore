from datetime import datetime, timezone

from app.modules.users.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db):
        self.db = db
        self.repo = UserRepository(db)

    async def get_by_id(self, user_id: int):
        return await self.repo.get_by_id(user_id)

    async def delete_user(self, user_id: int) -> bool:
        """Soft-delete (deactivate) a user's own account."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            return False
        user.is_active = False
        user.deleted_at = datetime.now(timezone.utc)
        self.db.add(user)
        await self.db.commit()
        return True
