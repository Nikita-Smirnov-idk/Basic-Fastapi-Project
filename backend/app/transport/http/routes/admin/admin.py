from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.domain.exceptions import (
    AdminCannotDeleteSelfError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.transport.http.deps import AdminUseCaseDep
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
    user_in: PrivateUserCreate, admin: AdminDep, admin_use_case: AdminUseCaseDep
) -> Any:
    """Create a new user."""
    try:
        user = await admin_use_case.create_user(
            email=user_in.email,
            password=user_in.password,
            full_name=user_in.full_name,
            is_verified=user_in.is_verified,
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    return UserPublic.model_validate(user)


@router.get("/", response_model=UsersPublic)
async def read_users(
    admin: AdminDep, admin_use_case: AdminUseCaseDep, skip: int = 0, limit: int = 100
) -> Any:
    """Retrieve users."""
    users_list, count = await admin_use_case.get_users(skip=skip, limit=limit)
    return UsersPublic(
        data=[UserPublic.model_validate(u) for u in users_list],
        count=count,
    )


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    user_id: uuid.UUID, admin: AdminDep, admin_use_case: AdminUseCaseDep
) -> Any:
    """Get a specific user by id."""
    try:
        user = await admin_use_case.get_user_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return UserPublic.model_validate(user)


@router.delete("/{user_id}")
async def delete_user(
    admin: AdminDep, admin_use_case: AdminUseCaseDep, user_id: uuid.UUID
) -> Message:
    """Delete a user."""
    try:
        await admin_use_case.delete_user(admin_id=admin.id, user_id=user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except AdminCannotDeleteSelfError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    return Message(message="User deleted successfully")
