import logging
from typing import Optional, Any

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from sqlmodel import select

from app.models.db.models import User
from app.models.users.models import UserCreate, UserUpdate
from app.services.passwords.utils import get_password_hash, verify_password


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # --------- Create ---------

    def create_by_password(self, user_create: UserCreate) -> User:
        user = User.model_validate(
            user_create,
            update={"hashed_password": get_password_hash(user_create.password)},
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

    # --------- Read ---------

    def get_by_id(self, user_id: Any) -> Optional[User]:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return self.session.exec(stmt).first()

    def get_by_google_id(self, google_id: str) -> Optional[User]:
        stmt = select(User).where(User.google_id == google_id)
        return self.session.exec(stmt).first()

    # --------- Auth ---------

    def authenticate(self, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(email)
        if not user:
            return None
        if not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    # --------- Update ---------

    def update(self, *, user: User, user_in: UserUpdate) -> User:
        data = user_in.model_dump(exclude_unset=True)
        extra_data = {}

        if "password" in data:
            extra_data["hashed_password"] = get_password_hash(data.pop("password"))

        user.sqlmodel_update(data, update=extra_data)
        self.session.add(user)

        return user
    
    def change_password(self, *, user: User, new_password) -> User:
        hashed_password = get_password_hash(password=new_password)
        user.hashed_password = hashed_password
        self.session.add(user)

        return user

    def link_google_id(self, *, user: User, google_id: str) -> User:
        user.google_id = google_id
        self.session.add(user)
        
        return user
