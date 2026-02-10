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
from sqlalchemy.exc import IntegrityError
from sqlmodel import func, select

from app.domain.entities.db.user import User
from app.infrastructure.passwords.utils import get_password_hash
from app.transport.http.deps import SessionDep, CurrentUser
from app.transport.http.routes.admin.deps import AdminDep
from app.transport.schemas import Message, UserPublic, UsersPublic

router = APIRouter(tags=["admin"], prefix="/admin")


class PrivateUserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    is_verified: bool = False
    plan: str = "free"
    balance_cents: int = 0


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


class BalanceUpdate(BaseModel):
    amount_cents: int


@router.post("/{user_id}/balance", response_model=UserPublic)
async def update_user_balance(
    user_id: uuid.UUID,
    body: BalanceUpdate,
    session: SessionDep,
    admin: AdminDep,
) -> Any:
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.balance_cents = max(0, user.balance_cents + body.amount_cents)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


class AdminDashboardStats(BaseModel):
    total_users: int
    paying_users: int
    total_balance_cents: int
    yc_companies_count: int
    yc_founders_count: int


@router.get("/dashboard", response_model=AdminDashboardStats)
async def admin_dashboard(
    session: SessionDep,
    admin: AdminDep,
) -> AdminDashboardStats:
    users_count = await session.execute(select(func.count()).select_from(User))
    total_users = int(users_count.scalar_one())

    paying_stmt = select(func.count()).select_from(User).where(User.plan != "free")
    paying_result = await session.execute(paying_stmt)
    paying_users = int(paying_result.scalar_one())

    balance_stmt = select(func.coalesce(func.sum(User.balance_cents), 0))
    balance_result = await session.execute(balance_stmt)
    total_balance_cents = int(balance_result.scalar_one() or 0)

    from app.domain.entities.db.yc_company import YCCompany  # local import to avoid cycle
    from app.domain.entities.db.yc_founder import YCFounder  # local import to avoid cycle

    yc_stmt = select(func.count()).select_from(YCCompany)
    yc_result = await session.execute(yc_stmt)
    yc_companies_count = int(yc_result.scalar_one())

    ycf_stmt = select(func.count()).select_from(YCFounder)
    ycf_result = await session.execute(ycf_stmt)
    yc_founders_count = int(ycf_result.scalar_one())

    return AdminDashboardStats(
        total_users=total_users,
        paying_users=paying_users,
        total_balance_cents=total_balance_cents,
        yc_companies_count=yc_companies_count,
        yc_founders_count=yc_founders_count,
    )
