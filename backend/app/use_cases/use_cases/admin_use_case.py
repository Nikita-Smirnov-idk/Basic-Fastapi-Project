"""
Admin use case: create user, list users, get user by id, delete user.
Depends only on ports (IUnitOfWork).
Raises domain exceptions; transport maps to HTTP.
"""
from uuid import UUID

from app.domain.exceptions import (
    AdminCannotDeleteSelfError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.use_cases.ports.unit_of_work import IUnitOfWork


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
            if user.id == admin_id:
                raise AdminCannotDeleteSelfError(
                    "Super users are not allowed to delete themselves"
                )
            await uow.users.delete(user)
            await uow.commit()
