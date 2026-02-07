"""
Google Auth use case: process_google_oauth_callback.
Depends only on ports (IUnitOfWork, IRefreshTokenStore, ITokenService).
Raises domain exceptions; transport maps to HTTP.
"""
import logging
from typing import Any

from app.use_cases.ports.refresh_store import IRefreshTokenStore
from app.use_cases.ports.token_service import ITokenService
from app.use_cases.ports.unit_of_work import IUnitOfWork
from app.use_cases.use_cases.token_helpers import create_and_store_tokens
from app.domain.exceptions import InvalidCredentialsError, InactiveUserError

logger = logging.getLogger(__name__)


class GoogleAuthUseCase:
    def __init__(
        self,
        uow: IUnitOfWork,
        refresh_store: IRefreshTokenStore,
        token_service: ITokenService,
    ):
        self._uow = uow
        self._refresh_store = refresh_store
        self._token_service = token_service

    async def process_google_oauth_callback(
        self,
        google_id: str,
        email: str,
        full_name: str | None,
        user_agent: str,
    ) -> dict[str, Any]:
        async with self._uow as uow:
            user = await uow.users.get_by_google_id(google_id)
            if user:
                logger.info("Google login (existing google_id), user_id=%s", user.id)
                return await self._create_tokens(user, user_agent)
            existing_user = await uow.users.get_by_email(email)
            if existing_user:
                if not existing_user.hashed_password:
                    raise InvalidCredentialsError(
                        "Failed to link Google account. This account uses another authentication method without password."
                    )
                if not existing_user.is_verified:
                    raise InvalidCredentialsError(
                        "Cannot link Google account. Email is not verified. "
                        "Please verify your email first (via original registration method)."
                    )
                user = uow.users.link_google_id(user=existing_user, google_id=google_id)
                logger.info("Google account linked, user_id=%s", user.id)
            else:
                user = uow.users.create_by_google(
                    email=email,
                    google_id=google_id,
                    full_name=full_name,
                    is_verified=True,
                )
                logger.info("New user via Google OAuth, user_id=%s", user.id)
            await uow.commit()
            return await self._create_tokens(user, user_agent)

    async def _create_tokens(self, user: Any, user_agent: str) -> dict[str, Any]:
        if not user.is_active:
            raise InactiveUserError("Inactive user")
        return await create_and_store_tokens(
            self._token_service,
            self._refresh_store,
            str(user.id),
            user_agent,
        )
