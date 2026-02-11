"""
Admin use case: create user, list users, get user by id, delete user, dashboard stats, balance update.
Depends only on ports (IUnitOfWork).
Raises domain exceptions; transport maps to HTTP.
"""
import logging
from uuid import UUID

from app.domain.exceptions import (
    AdminCannotBeDeletedError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.use_cases.ports.admin_stats_repository import AdminDashboardStatsData
from app.use_cases.ports.unit_of_work import IUnitOfWork


logger = logging.getLogger(__name__)


class AdminUseCase:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def create_user(
        self,
        *,
        email: str,
        password: str,
        full_name: str,
        is_verified: bool = False,
    ) -> object:
        async with self._uow as uow:
            existing = await uow.users.get_by_email(email)
            if existing:
                raise UserAlreadyExistsError("User with this email already exists")
            user = uow.users.create_by_password(
                email=email,
                password=password,
                full_name=full_name,
                is_verified=is_verified,
            )
            await uow.commit()
            return user

    async def get_users(self, *, skip: int = 0, limit: int = 100) -> tuple[list[object], int]:
        async with self._uow as uow:
            users, count = await uow.users.get_list(skip=skip, limit=limit)
            return (users, count)

    async def get_user_by_id(self, user_id: UUID) -> object:
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFoundError("User not found")
            return user

    async def delete_user(self, *, admin_id: UUID, user_id: UUID) -> None:
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFoundError("User not found")
            if user.id == admin_id or user.is_superuser:
                raise AdminCannotBeDeletedError(
                    "Admin users can not be deleted"
                )
            await uow.users.delete(user)
            await uow.commit()
            logger.info("Admin with id=%s, deleted user with user_id=%s", admin_id, user_id)

    async def get_dashboard_stats(self) -> AdminDashboardStatsData:
        async with self._uow as uow:
            return await uow.admin_stats.get_dashboard_stats()

    async def update_user_balance(
        self, *, admin_id: UUID, user_id: UUID, amount_cents: int
    ) -> object:
        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFoundError("User not found")
            new_balance = max(0, user.balance_cents + abs(amount_cents))
            uow.users.update(user=user, data={"balance_cents": new_balance})
            await uow.commit()
            logger.info("Admin with id=%s added balance to user with user_id=%s amout=%s", admin_id, user_id, amount_cents)
            return user
