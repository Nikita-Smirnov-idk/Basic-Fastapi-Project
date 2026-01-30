"""Unit of work: session + repositories. Implements use_cases.ports.IUnitOfWork."""
from __future__ import annotations

from typing import TYPE_CHECKING

from app.infrastructure.persistence.postgres.repositories.user_repository import (
    UserRepository,
)
from app.use_cases.ports.unit_of_work import IUnitOfWork
from app.use_cases.ports.user_repository import IUserRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork(IUnitOfWork):
    def __init__(self, session: "AsyncSession") -> None:
        self._session = session
        self.users: IUserRepository = UserRepository(session)

    async def __aenter__(self) -> UnitOfWork:
        return self

    async def __aexit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        if exc_type is not None:
            await self._session.rollback()
        else:
            await self._session.commit()
        return None

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
