"""
User use case: get_me, delete_me.
Depends only on ports (IUnitOfWork).
Raises domain exceptions; transport maps to HTTP.
"""
import logging
from uuid import UUID

from app.use_cases.ports.unit_of_work import IUnitOfWork
from app.domain.entities.user import User as DomainUser
from app.domain.exceptions import UserNotFoundError

logger = logging.getLogger(__name__)


class UserUseCase:
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def get_me(self, user_id: UUID) -> DomainUser:
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFoundError("User not found")
            return DomainUser.model_validate(user)

    async def delete_me(self, user_id: UUID) -> None:
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFoundError("User not found")
            await uow.users.delete(user)
            await uow.commit()
        logger.info("User deleted, user_id=%s", user_id)
