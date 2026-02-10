from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import col, delete, func, select

from app.domain.entities.db.user import Item, User
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
    user_in: PrivateUserCreate, session: SessionDep, admin: AdminDep
) -> Any:
    """Create a new user."""
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        is_verified=user_in.is_verified,
        plan=user_in.plan,
        balance_cents=user_in.balance_cents,
    )
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        ) from None
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
