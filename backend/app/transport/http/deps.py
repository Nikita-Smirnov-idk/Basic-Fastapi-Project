"""
Transport dependencies: session, UoW, use cases, current user.
Wires infrastructure implementations to application use cases.
"""
import logging
from datetime import timedelta
from typing import Annotated

from fastapi import Cookie, Depends, Header, HTTPException, Security, status
from fastapi.security import APIKeyCookie, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.use_cases.ports.refresh_store import IRefreshTokenStore
from app.use_cases.ports.token_service import ITokenService
from app.use_cases.use_cases.admin_use_case import AdminUseCase
from app.use_cases.use_cases.auth_use_case import AuthUseCase
from app.use_cases.use_cases.google_auth_use_case import GoogleAuthUseCase
from app.use_cases.use_cases.password_use_case import PasswordUseCase
from app.use_cases.use_cases.user_use_case import UserUseCase
from app.core.config.config import settings
from app.infrastructure.email.email_sender import EmailSender, get_email_sender
from app.infrastructure.jwt.token_service import TokenService, get_token_service
from app.domain.entities.db.user import User as DBUser
from app.infrastructure.persistence.postgres.repositories.yc_directory_repository import (
    YCDirectoryRepository,
)
from app.infrastructure.persistence.postgres.session import get_async_session
from app.infrastructure.persistence.postgres.unit_of_work import UnitOfWork
from app.infrastructure.redis.redis_repo import RedisRepository, get_redis_repo
from app.use_cases.use_cases.yc_directory_use_case import YCDirectoryUseCase

logger = logging.getLogger(__name__)

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]

access_cookie = APIKeyCookie(name="access_token", auto_error=False)

async def get_access_token(
    token: str = Security(access_cookie),
) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return token
TokenDep = Annotated[str, Depends(get_access_token)]


def get_uow(session: SessionDep) -> UnitOfWork:
    return UnitOfWork(session)


def get_auth_use_case(
    uow: UnitOfWork = Depends(get_uow),
    refresh_store: RedisRepository = Depends(get_redis_repo),
    token_service: TokenService = Depends(get_token_service),
    email_sender: EmailSender = Depends(get_email_sender),
) -> AuthUseCase:
    return AuthUseCase(
        uow=uow,
        refresh_store=refresh_store,
        token_service=token_service,
        email_sender=email_sender,
        emails_enabled=settings.emails_enabled,
    )


def get_password_use_case(
    uow: UnitOfWork = Depends(get_uow),
    token_service: TokenService = Depends(get_token_service),
    email_sender: EmailSender = Depends(get_email_sender),
) -> PasswordUseCase:
    return PasswordUseCase(
        uow=uow,
        token_service=token_service,
        email_sender=email_sender,
        emails_enabled=settings.emails_enabled,
    )


def get_user_use_case(uow: UnitOfWork = Depends(get_uow)) -> UserUseCase:
    return UserUseCase(uow=uow)


def get_admin_use_case(uow: UnitOfWork = Depends(get_uow)) -> AdminUseCase:
    return AdminUseCase(uow=uow)


def get_google_auth_use_case(
    uow: UnitOfWork = Depends(get_uow),
    refresh_store: RedisRepository = Depends(get_redis_repo),
    token_service: TokenService = Depends(get_token_service),
) -> GoogleAuthUseCase:
    return GoogleAuthUseCase(
        uow=uow,
        refresh_store=refresh_store,
        token_service=token_service,
    )


async def get_current_user(
    session: SessionDep,
    token: TokenDep,
    token_service: Annotated[ITokenService, Depends(get_token_service)],
) -> DBUser:
    try:
        user_id = token_service.verify_token_and_get_sub(token, "access")
    except ValueError as e:
        logger.warning("Invalid credentials: %s", e)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from e
    user = await session.get(DBUser, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


def get_user_agent(user_agent: str | None = Header(default=None)) -> str:
    return user_agent if user_agent else "Unknown user agent"


def get_refresh_token_from_cookie(
    refresh_token: str | None = Cookie(default=None, alias="refresh_token"),
) -> str | None:
    return refresh_token


CurrentUser = Annotated[DBUser, Depends(get_current_user)]


def get_current_active_superuser(current_user: DBUser = Depends(get_current_user)) -> DBUser:
    if not current_user.is_superuser:
        logger.warning("Insufficient privileges, user_id=%s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


def get_yc_directory_repo(session: SessionDep) -> YCDirectoryRepository:
    return YCDirectoryRepository(session)


def get_yc_use_case(
    repo: Annotated[YCDirectoryRepository, Depends(get_yc_directory_repo)],
) -> YCDirectoryUseCase:
    return YCDirectoryUseCase(
        repo=repo,
        auto_sync_interval=timedelta(days=settings.YC_AUTO_SYNC_DAYS),
    )

YCDirectoryUseCaseDep = Annotated[YCDirectoryUseCase, Depends(get_yc_use_case)]
UserAgentDep = Annotated[str, Depends(get_user_agent)]
RefreshTokenDep = Annotated[str | None, Depends(get_refresh_token_from_cookie)]
AuthUseCaseDep = Annotated[AuthUseCase, Depends(get_auth_use_case)]
PasswordUseCaseDep = Annotated[PasswordUseCase, Depends(get_password_use_case)]
UserUseCaseDep = Annotated[UserUseCase, Depends(get_user_use_case)]
AdminUseCaseDep = Annotated[AdminUseCase, Depends(get_admin_use_case)]
GoogleAuthUseCaseDep = Annotated[GoogleAuthUseCase, Depends(get_google_auth_use_case)]
