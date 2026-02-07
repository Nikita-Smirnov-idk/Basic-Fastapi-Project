"""
Auth use case: login, signup, refresh, logout, sessions.
Depends only on ports (IUnitOfWork, IRefreshTokenStore, ITokenService, IEmailSender).
Raises domain exceptions; transport maps to HTTP.
"""
import logging
from typing import Any

from app.use_cases.ports.refresh_store import IRefreshTokenStore
from app.use_cases.ports.token_service import ITokenService
from app.use_cases.ports.unit_of_work import IUnitOfWork
from app.use_cases.ports.email_sender import IEmailSender
from app.use_cases.use_cases.token_helpers import create_and_store_tokens
from app.domain.entities.pydantic.user import User as DomainUser
from app.domain.exceptions import (
    InvalidCredentialsError,
    InactiveUserError,
    UserAlreadyExistsError,
)

logger = logging.getLogger(__name__)


class AuthUseCase:
    def __init__(
        self,
        uow: IUnitOfWork,
        refresh_store: IRefreshTokenStore,
        token_service: ITokenService,
        email_sender: IEmailSender,
        emails_enabled: bool,
    ):
        self._uow = uow
        self._refresh_store = refresh_store
        self._token_service = token_service
        self._email_sender = email_sender
        self._emails_enabled = emails_enabled

    async def login(self, email: str, password: str, user_agent: str) -> dict[str, Any]:
        async with self._uow as uow:
            user = await uow.users.authenticate(email=email, password=password)
            if not user:
                raise InvalidCredentialsError("Incorrect username or password")
            if not user.is_active:
                raise InactiveUserError("Inactive user")
            return await create_and_store_tokens(
                self._token_service, self._refresh_store, str(user.id), user_agent
            )

    async def start_signup(self, email: str) -> None:
        async with self._uow as uow:
            if await uow.users.get_by_email(email):
                return
        signup_token = self._token_service.create_signup_token({"sub": email})
        if self._emails_enabled:
            self._email_sender.send_signup_confirmation(email=email, token=signup_token)
            logger.info("Signup email sent to %s", email)
        else:
            logger.info("Emails disabled, skipping signup email for %s", email)

    async def complete_signup(
        self, token: str, password: str, full_name: str | None
    ) -> DomainUser:
        try:
            payload = self._token_service.decode_and_validate(token, "signup")
            email = self._token_service.get_sub(payload)
        except ValueError:
            raise InvalidCredentialsError("Invalid token")
        if not isinstance(email, str) or "@" not in email:
            raise InvalidCredentialsError("Invalid token payload")
        async with self._uow as uow:
            if await uow.users.get_by_email(email):
                raise UserAlreadyExistsError("User with this email already exists")
            user = uow.users.create_by_password(
                email=email,
                password=password,
                full_name=full_name,
                is_verified=True,
            )
            await uow.commit()
            return DomainUser.model_validate(user)

    async def refresh(self, refresh_token: str, user_agent: str) -> dict[str, Any]:
        try:
            payload = self._token_service.decode_and_validate(refresh_token, "refresh")

            user_id = self._token_service.get_sub(payload)
            token_jti = self._token_service.get_jti(payload)
            family_id = self._token_service.get_family_id(payload)
        except ValueError:
            raise InvalidCredentialsError("Invalid refresh token")
        
        refresh_data = await self._refresh_store.get_refresh_data(token_jti)

        try:
            self._token_service.compare_refresh_payload_and_stored_data(payload, refresh_data)
        except ValueError:
            logger.warning("Failed refresh: invalid payload, user_id=%s, token_jti=%s", user_id, token_jti)
            raise InvalidCredentialsError("Invalid refresh token")
        
        if refresh_data["user_agent"] != user_agent:
            logger.warning("Failed refresh: invalid data, user_id=%s, token_jti=%s", user_id, token_jti)
            await self._refresh_store.block_refresh(token_jti)
            if "family_id" in refresh_data:
                await self._refresh_store.block_family(
                    family_id, user_id
                )
            raise InvalidCredentialsError("Invalid Token")
        
        if await self._refresh_store.is_refresh_blocked(token_jti):
            if "family_id" in refresh_data:
                await self._refresh_store.block_family(family_id, user_id)

            logger.warning("Failed refresh: blocked, user_id=%s, token_jti=%s", user_id, token_jti)
            raise InvalidCredentialsError("Invalid Token")
        
        if await self._refresh_store.is_family_blocked(family_id):
            await self._refresh_store.block_refresh(token_jti)
            logger.warning("Failed refresh: family blocked, user_id=%s, token_jti=%s", user_id, token_jti)
            raise InvalidCredentialsError("Invalid Token")

        if not await self._refresh_store.try_block_refresh(token_jti):
            if "family_id" in refresh_data:
                await self._refresh_store.block_family(
                    family_id, user_id
                )
            logger.warning("Failed refresh: token reuse, user_id=%s", user_id)
            raise InvalidCredentialsError("Invalid Token")

        logger.info("Starting to create tokens for refresh/, user_id=%s, token_jti=%s", user_id, token_jti)
        return await create_and_store_tokens(
            self._token_service, self._refresh_store, user_id, user_agent, family_id
        )

    async def logout(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return
        try:
            payload = self._token_service.decode_and_validate(refresh_token, "refresh")
            token_jti = payload.get("jti")
            if not token_jti:
                return
        except ValueError:
            return
        refresh_data = await self._refresh_store.get_refresh_data(token_jti)
        if refresh_data:
            await self._refresh_store.block_refresh(token_jti)
            if "family_id" in refresh_data:
                await self._refresh_store.block_family(
                    refresh_data["family_id"], refresh_data["user_id"]
                )
            logger.info("Logout, user_id=%s", refresh_data["user_id"])

    async def get_sessions(self, user_id: str) -> list[dict[str, Any]]:
        sessions_dict = await self._refresh_store.get_sessions_by_user_id(user_id)
        active = []
        for family_id, data in sessions_dict.items():
            if not data.get("blocked", False):
                active.append({
                    "family_id": family_id,
                    "user_agent": data.get("user_agent", "Unknown"),
                    "created_at": data.get("created_at", ""),
                    "last_active": data.get("last_active", ""),
                })
        active.sort(key=lambda x: x["last_active"], reverse=True)
        return active

    async def block_session(self, user_id: str, family_id: str) -> None:
        sessions = await self._refresh_store.get_sessions_by_user_id(user_id)
        if family_id not in sessions:
            raise InvalidCredentialsError("This session does not belong to you")
        await self._refresh_store.block_family(family_id, user_id)
        logger.info("Session blocked, user_id=%s family_id=%s", user_id, family_id)

    async def block_all_sessions(self, user_id: str) -> int:
        sessions = await self._refresh_store.get_sessions_by_user_id(user_id)
        count = 0
        for family_id in list(sessions.keys()):
            await self._refresh_store.block_family(family_id, user_id)
            count += 1
        logger.info("All sessions blocked, user_id=%s count=%s", user_id, count)
        return count
