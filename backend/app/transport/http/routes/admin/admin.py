from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import col, delete, func, select

from app.infrastructure.persistence.models import Item, User
from app.infrastructure.passwords.utils import get_password_hash
from app.transport.http.deps import SessionDep
from app.transport.http.routes.admin.deps import AdminDep
from app.transport.schemas import Message, UserPublic, UsersPublic

router = APIRouter(tags=["admin"], prefix="/admin")


class PrivateUserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    is_verified: bool = False


@router.post("/", response_model=UserPublic)
async def create_user(
    user_in: PrivateUserCreate, session: SessionDep, admin: AdminDep
) -> Any:
    """Create a new user."""
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.get("/", response_model=UsersPublic)
async def read_users(
    session: SessionDep, admin: AdminDep, skip: int = 0, limit: int = 100
) -> Any:
    """Retrieve users."""
    count_statement = select(func.count()).select_from(User)
    count_result = await session.execute(count_statement)
    count = count_result.scalar_one()
    statement = select(User).offset(skip).limit(limit)
    result = await session.execute(statement)
    users_list = result.scalars().all()
    return UsersPublic(data=users_list, count=count)


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, admin: AdminDep
) -> Any:
    """Get a specific user by id."""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}")
async def delete_user(
    session: SessionDep, admin: AdminDep, user_id: uuid.UUID
) -> Message:
    """Delete a user."""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super users are not allowed to delete themselves",
        )
    stmt = delete(Item).where(col(Item.owner_id) == user_id)
    await session.execute(stmt)
    await session.delete(user)
    await session.commit()
    return Message(message="User deleted successfully")
