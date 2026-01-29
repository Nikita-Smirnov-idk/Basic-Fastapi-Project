import logging
from typing import Optional, Dict, List

from fastapi import HTTPException, status

from app.models.users.models import UserCreate, UserPublic, SessionOut
from app.services.jwt import tokens
from app.db.postgres.unit_of_work import UnitOfWork
from app.models.db.models import User
from app.db.redis.redis_repo import RedisRepository
from app.utils import generate_signup_confirmation_email, send_email
from app.core.config import settings
from app.services.users.utils import create_and_store_tokens

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, uow: UnitOfWork, redis_repo: RedisRepository):
        self.uow = uow
        self.redis = redis_repo

    # ---------------- Login ----------------
    async def login(self, email: str, password: str, user_agent: str) -> Dict[str, str]:
        async with self.uow as uow:
            user: User = uow.users.authenticate(email=email, password=password)
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
            if not user.is_active:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

            return await create_and_store_tokens(self.redis, user.id, user_agent)

    # ---------------- Start Signup ----------------
    async def start_signup(self, email: str) -> None:
        async with self.uow as uow:
            if uow.users.get_by_email(email):
                # Не выдаем информацию о существовании пользователя
                return

        # Генерируем JWT токен для подтверждения email
        signup_token = tokens.create_signup_token({"sub": email})

        # Отправка письма, если включена
        if settings.emails_enabled:
            email_data = generate_signup_confirmation_email(email=email, token=signup_token)
            send_email(
                email_to=email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )
            logger.info("Signup email sent to %s", email)
        else:
            logger.info("Emails disabled, skipping sending signup email for %s", email)

    # ---------------- Complete Signup ----------------
    async def complete_signup(self, token: str, password: str, full_name: Optional[str]) -> UserPublic:
        try:
            payload = tokens.decode_token(token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token"
            )
        
        await self._check_token_payload(payload, "signup")

        email = payload.get("sub")
        if not email or not isinstance(email, str) or "@" not in email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token payload")


        async with self.uow as uow:
            if uow.users.get_by_email(email):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
            user_create = UserCreate(
                email=email,
                password=password,
                full_name=full_name,
                is_verified=True
            )
            user = uow.users.create_by_password(user_create)
            await uow.commit()
            return user

    # ---------------- Refresh Token ----------------
    async def refresh(self, refresh_token: str, user_agent: str) -> Dict[str, str]:
        try:
            payload = tokens.decode_token(refresh_token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid refresh token"
            )
        
        await self._check_token_payload(payload, "refresh")

        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid refresh token"
            )
        user_id = str(user_id_raw)
        
        refresh_data = await self.redis.get_refresh_data(refresh_token)

        # Проверки безопасности
        if not refresh_data or \
            str(refresh_data["user_id"]) != user_id or \
            refresh_data["user_agent"] != user_agent:
                logger.warning("Failed to get new refresh: Invalid data, user_id=%s", user_id)
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Token")

        if await self.redis.is_refresh_blocked(refresh_token):
            if "family_id" in refresh_data:
                await self.redis.block_family(refresh_data["family_id"], user_id)
            logger.warning("Failed to get new refresh: Refresh blocked, user_id=%s", user_id)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Token")

        if await self.redis.is_family_blocked(refresh_data["family_id"]):
            logger.warning("Failed to get new refresh: Family blocked, user_id=%s", user_id)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Token")


        # Ротация
        await self.redis.block_refresh(refresh_token)
        return await create_and_store_tokens(self.redis, user_id, user_agent)

    # ---------------- Logout ----------------
    async def logout(self, refresh_token: Optional[str]) -> None:
        if not refresh_token:
            return
        refresh_data = await self.redis.get_refresh_data(refresh_token)
        if refresh_data:
            await self.redis.block_refresh(refresh_token)
            if "family_id" in refresh_data:
                await self.redis.block_family(refresh_data["family_id"], refresh_data["user_id"])
            logger.info("Logout, user_id=%s", refresh_data["user_id"])

    # ---------------- Get active sessions ----------------
    async def get_sessions(self, user_id: str) -> List[SessionOut]:
        sessions_dict = await self.redis.get_sessions_by_user_id(user_id)
        active_sessions = []
        for family_id, data in sessions_dict.items():
            if not data.get("blocked", False):
                active_sessions.append(
                    SessionOut(
                        family_id=family_id,
                        user_agent=data.get("user_agent", "Unknown"),
                        created_at=data.get("created_at", ""),
                        last_active=data.get("last_active", ""),
                    )
                )
        active_sessions.sort(key=lambda x: x.last_active, reverse=True)
        return active_sessions

    # ---------------- Block specific session ----------------
    async def block_session(self, user_id: str, family_id: str) -> None:
        sessions = await self.redis.get_sessions_by_user_id(user_id)
        if family_id not in sessions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This session does not belong to you")
        await self.redis.block_family(family_id, user_id)
        logger.info("Session blocked, user_id=%s family_id=%s", user_id, family_id)

    # ---------------- Block all sessions ----------------
    async def block_all_sessions(self, user_id: str) -> None:
        sessions = await self.redis.get_sessions_by_user_id(user_id)
        count = 0
        for family_id in list(sessions.keys()):
            await self.redis.block_family(family_id, user_id)
            count += 1
        logger.info("All sessions blocked, user_id=%s count=%s", user_id, count)
        return count
        

    async def _check_token_payload(payload: Dict[str, str], check_type: str) -> None:
        if payload.get("type") != check_type:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token payload",
            )
        if payload.get("iss") != settings.FRONTEND_HOST:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token payload"
            )