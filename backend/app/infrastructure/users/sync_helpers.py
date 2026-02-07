"""Sync user helpers for scripts (init_db) and tests. Use primitives to avoid transport/schema deps."""
from typing import Any

from sqlmodel import Session, select

from app.infrastructure.passwords.utils import get_password_hash, verify_password
from app.domain.entities.db.user import User


def create_user_sync(
    session: Session,
    *,
    email: str,
    password: str,
    full_name: str | None = None,
    is_superuser: bool = False,
    is_verified: bool = False,
    is_active: bool = True,
) -> User:
    """Create user with hashed password (sync). For scripts and tests only."""
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        is_superuser=is_superuser,
        is_verified=is_verified,
        is_active=is_active,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_email_sync(session: Session, email: str) -> User | None:
    """Get user by email (sync). For tests only."""
    stmt = select(User).where(User.email == email)
    return session.exec(stmt).first()


def update_user_sync(
    session: Session,
    db_user: User,
    *,
    data: dict[str, Any],
) -> User:
    """Update user (sync). For tests only. data may include 'password' (will be hashed)."""
    extra: dict[str, Any] = {}
    if "password" in data:
        extra["hashed_password"] = get_password_hash(data.pop("password"))
    db_user.sqlmodel_update(data, update=extra)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def authenticate_user_sync(
    session: Session,
    email: str,
    password: str,
) -> User | None:
    """Authenticate by email/password (sync). For tests only."""
    user = get_user_by_email_sync(session, email)
    if not user or not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
