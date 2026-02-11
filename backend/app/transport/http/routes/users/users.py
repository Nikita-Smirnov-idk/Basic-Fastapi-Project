from fastapi import APIRouter, HTTPException, Request, status

from app.core.config.config import settings
from app.domain.exceptions import UserNotFoundError
from app.transport.http.deps import CurrentUser
from app.transport.http.rate_limit import limiter, PER_ROUTE_LIMIT
from app.transport.http.routes.users.auth import auth
from app.transport.http.routes.users.deps import UserUseCaseDep
from app.transport.http.routes.users.google_auth import google_auth
from app.transport.http.routes.users.passwords import passwords
from app.transport.schemas import Message, UserPublic

router = APIRouter(prefix="/users", tags=["users"])

router.include_router(auth.router)
router.include_router(passwords.router)
if settings.GOOGLE_CLIENT_ID is not None and settings.GOOGLE_CLIENT_SECRET is not None:
    router.include_router(google_auth.router)


@router.get("/me", response_model=UserPublic)
@limiter.limit(PER_ROUTE_LIMIT)
async def read_user_me(request: Request, current_user: CurrentUser, user_use_case: UserUseCaseDep):
    try:
        domain_user = await user_use_case.get_me(current_user.id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return UserPublic.model_validate(domain_user)


@router.delete("/me", response_model=Message)
@limiter.limit(PER_ROUTE_LIMIT)
async def delete_user_me(request: Request, current_user: CurrentUser, user_use_case: UserUseCaseDep):
    if current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super users are not allowed to delete themselves",
        )
    try:
        await user_use_case.delete_me(current_user.id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return Message(message="User deleted successfully")
