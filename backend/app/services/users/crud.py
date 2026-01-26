import logging
import uuid
from typing import Any

from sqlmodel import Session, select

from app.models.db.models import User
from app.models.users.models import UserCreate, UserUpdate
from app.services.passwords.utils import get_password_hash, verify_password

logger = logging.getLogger(__name__)

def create_user_by_password(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    logger.info("User created, user_id=%s", db_obj.id)
    return db_obj

def create_user_by_google_id(
    *, session: Session, email: str, google_id: str, is_verified: bool = True, full_name: str | None = None
) -> User:
    db_obj = User(
        email=email,
        google_id=google_id,
        hashed_password=None,
        full_name=full_name,
        is_verified=is_verified,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    logger.info("User created via Google, user_id=%s", db_obj.id)
    return db_obj


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def get_user_by_google_id(*, session: Session, google_id: str) -> User | None:
    statement = select(User).where(User.google_id == google_id)
    return session.exec(statement).first()

def link_google_id(*, session: Session, user: User, google_id: str) -> User:
    user.google_id = google_id
    session.add(user)
    session.commit()
    session.refresh(user)
    logger.info("Google linked, user_id=%s", user.id)
    return user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not db_user.hashed_password:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    logger.info("User updated, user_id=%s", db_user.id)
    return db_user