from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.domain.exceptions import (
    AdminCannotBeDeletedError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.transport.http.deps import AdminUseCaseDep
from app.transport.http.rate_limit import limiter, PER_ROUTE_LIMIT
from app.transport.http.routes.admin.deps import AdminDep
from app.transport.schemas import (
    Message,
    UserPublic,
    UsersPublic,
    PrivateUserCreate,
    AdminDashboardStats,
    BalanceUpdate,
    YCSyncStatePublic,
)
from app.transport.http.routes.yc.deps import YCDirectoryUseCaseDep

router = APIRouter(tags=["admin"], prefix="/admin")


@router.post("/", response_model=UserPublic)
@limiter.limit(PER_ROUTE_LIMIT)
async def create_user(
    request: Request,
    user_in: PrivateUserCreate,
    admin: AdminDep,
    admin_use_case: AdminUseCaseDep,
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
@limiter.limit(PER_ROUTE_LIMIT)
async def read_users(
    request: Request,
    admin: AdminDep,
    admin_use_case: AdminUseCaseDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve users."""
    users_list, count = await admin_use_case.get_users(skip=skip, limit=limit)
    return UsersPublic(
        data=[UserPublic.model_validate(u) for u in users_list],
        count=count,
    )


@router.get("/dashboard", response_model=AdminDashboardStats)
@limiter.limit(PER_ROUTE_LIMIT)
async def admin_dashboard(
    request: Request,
    admin: AdminDep,
    admin_use_case: AdminUseCaseDep,
) -> AdminDashboardStats:
    stats = await admin_use_case.get_dashboard_stats()
    return AdminDashboardStats(
        total_users=stats.total_users,
        paying_users=stats.paying_users,
        total_balance_cents=stats.total_balance_cents,
        yc_companies_count=stats.yc_companies_count,
        yc_founders_count=stats.yc_founders_count,
    )


@router.get("/{user_id}", response_model=UserPublic)
@limiter.limit(PER_ROUTE_LIMIT)
async def read_user_by_id(
    request: Request,
    user_id: uuid.UUID,
    admin: AdminDep,
    admin_use_case: AdminUseCaseDep,
) -> Any:
    """Get a specific user by id."""
    try:
        user = await admin_use_case.get_user_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return UserPublic.model_validate(user)


@router.delete("/{user_id}")
@limiter.limit(PER_ROUTE_LIMIT)
async def delete_user(
    request: Request,
    admin: AdminDep,
    admin_use_case: AdminUseCaseDep,
    user_id: uuid.UUID,
) -> Message:
    """Delete a user."""
    try:
        await admin_use_case.delete_user(admin_id=admin.id, user_id=user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except AdminCannotBeDeletedError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    return Message(message="User deleted successfully")


@router.post("/{user_id}/balance", response_model=UserPublic)
@limiter.limit(PER_ROUTE_LIMIT)
async def update_user_balance(
    request: Request,
    user_id: uuid.UUID,
    body: BalanceUpdate,
    admin: AdminDep,
    admin_use_case: AdminUseCaseDep,
) -> Any:
    try:
        user = await admin_use_case.update_user_balance(
            admin_id=admin.id,
            user_id=user_id,
            amount_cents=body.amount_cents,
        )
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    return UserPublic.model_validate(user)




@router.post("/sync", response_model=Message)
@limiter.limit(PER_ROUTE_LIMIT)
async def sync_now(
    request: Request,
    admin: AdminDep,
    yc_uc: YCDirectoryUseCaseDep,
) -> Message:
    count = await yc_uc.sync_from_source()
    return Message(message=f"Synced {count} YC companies")


@router.get("/sync-state", response_model=YCSyncStatePublic)
@limiter.limit(PER_ROUTE_LIMIT)
async def get_sync_state(
    request: Request,
    admin: AdminDep,
    yc_uc: YCDirectoryUseCaseDep,
) -> YCSyncStatePublic:
    state = await yc_uc.get_sync_state()
    if not state:
        return YCSyncStatePublic(
            last_started_at=None,
            last_finished_at=None,
            last_success_at=None,
            last_error=None,
            last_item_count=None,
        )
    return YCSyncStatePublic(
        last_started_at=state.last_started_at,
        last_finished_at=state.last_finished_at,
        last_success_at=state.last_success_at,
        last_error=state.last_error,
        last_item_count=state.last_item_count,
    )
