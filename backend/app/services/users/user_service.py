import logging

from fastapi import HTTPException

from app.db.postgres.unit_of_work import UnitOfWork
from app.models.db.models import User

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_me(self, user_id: str) -> User:
        async with self.uow as uow:
            user = uow.users.get(user_id)
            if not user:
                raise HTTPException(404, "User not found")
            return user

    async def delete_me(self, user_id: str) -> None:
        async with self.uow as uow:
            user = uow.users.get(user_id)
            if not user:
                raise HTTPException(404, "User not found")
            if user.is_superuser:
                raise HTTPException(403, "Super users are not allowed to delete themselves")
            uow.users.delete(user)
            await uow.commit()