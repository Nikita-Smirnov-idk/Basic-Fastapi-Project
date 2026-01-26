from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps import SessionDep, get_current_active_superuser
from app.services.passwords.utils import get_password_hash
from app.models.users.models import (
    UserPublic,
    UsersPublic,
)
from app.models.db.models import User
from app.services.passwords.utils import get_password_hash

from sqlmodel import func, select
from app.api.deps import AdminDep
from app.models.general.models import Message
from app.models.db.models import Item
from sqlmodel import col, delete

router = APIRouter(tags=["admin"], prefix="/admin")


class PrivateUserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    is_verified: bool = False


@router.post("/", response_model=UserPublic)
def create_user(user_in: PrivateUserCreate, session: SessionDep, admin: AdminDep) -> Any:
    """
    Create a new user.
    """

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )

    session.add(user)
    session.commit()

    return user

@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(session: SessionDep, admin: AdminDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)



@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: str, session: SessionDep, admin: AdminDep,
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    return user


@router.delete("/{user_id}")
def delete_user(
    session: SessionDep, admin: AdminDep, user_id: str
) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user == admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Super users are not allowed to delete themselves"
        )
    statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)  # type: ignore
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")
