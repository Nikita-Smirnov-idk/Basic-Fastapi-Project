"""User repository: persistence for User. Implements use_cases.ports.IUserRepository."""
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.infrastructure.passwords.utils import get_password_hash, verify_password
from app.infrastructure.persistence.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def create_by_password(
        self,
        *,
        email: str,
        password: str,
        full_name: str | None = None,
        is_verified: bool = False,
        is_superuser: bool = False,
    ) -> User:
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_verified=is_verified,
            is_superuser=is_superuser,
        )
        self.session.add(user)
        return user

    def create_by_google(
        self,
        *,
        email: str,
        google_id: str,
        is_verified: bool = True,
        full_name: str | None = None,
    ) -> User:
        user = User(
            email=email,
            google_id=google_id,
            hashed_password=None,
            full_name=full_name,
            is_verified=is_verified,
        )
        self.session.add(user)
        return user

    async def get_by_id(self, user_id: Any) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_google_id(self, google_id: str) -> User | None:
        stmt = select(User).where(User.google_id == google_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def authenticate(self, *, email: str, password: str) -> User | None:
        user = await self.get_by_email(email)
        if not user or not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def update(self, *, user: User, data: dict[str, Any]) -> User:
        extra: dict[str, Any] = {}
        if "password" in data:
            extra["hashed_password"] = get_password_hash(data.pop("password"))
        user.sqlmodel_update(data, update=extra)
        self.session.add(user)
        return user

    def change_password(self, *, user: User, new_password: str) -> User:
        user.hashed_password = get_password_hash(new_password)
        self.session.add(user)
        return user

    def link_google_id(self, *, user: User, google_id: str) -> User:
        user.google_id = google_id
        self.session.add(user)
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
