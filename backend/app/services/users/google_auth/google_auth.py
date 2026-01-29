import logging
from typing import Dict, Optional

from fastapi import HTTPException, status

from app.db.postgres.unit_of_work import UnitOfWork
from app.db.redis.redis_repo import RedisRepository
from app.models.db.models import User
from app.services.jwt import tokens
from app.core.config import settings
from app.services.users.utils import create_and_store_tokens

logger = logging.getLogger(__name__)


class GoogleAuthService:
    def __init__(self, uow: UnitOfWork, redis_repo: RedisRepository):
        self.uow = uow
        self.redis = redis_repo

    async def process_google_oauth_callback(
        self,
        google_id: str,
        email: str,
        full_name: Optional[str],
        user_agent: str,
    ) -> Dict[str, str]:
        """
        Основной метод обработки Google OAuth callback.
        
        Возвращает словарь с access_token, refresh_token (и user_id для лога)
        Логика:
        - Если google_id уже существует → обычный логин
        - Если есть пользователь с таким email:
          • с hashed_password и is_verified=True → привязываем google_id
          • без пароля или не верифицирован → ошибка 403
        - Если пользователя нет → создаём нового (is_verified=True)
        """
        async with self.uow as uow:
            # 1. Пытаемся найти по google_id
            user = uow.users.get_by_google_id(google_id)
            if user:
                logger.info("Google login (existing google_id), user_id=%s", user.id)
                return await self._create_tokens(uow, user, user_agent)

            # 2. Проверяем существование по email
            existing_user = uow.users.get_by_email(email)
            if existing_user:
                if not existing_user.hashed_password:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Failed to link Google account. This account uses another authentication method without password."
                    )

                if not existing_user.is_verified:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=(
                            "Cannot link Google account. Email is not verified. "
                            "Please verify your email first (via original registration method)."
                        )
                    )

                # Связываем
                user = uow.users.link_google_id(user=existing_user, google_id=google_id)
                logger.info("Google account linked to existing user, user_id=%s", user.id)

            else:
                # 3. Новый пользователь через Google
                user = uow.users.create_by_google(
                    email=email,
                    google_id=google_id,
                    full_name=full_name,
                    is_verified=True,
                )
                logger.info("New user created via Google OAuth, user_id=%s", user.id)

            # Фиксируем изменения в БД
            await uow.commit()

            return await self._create_tokens(user, user_agent)

    async def _create_tokens(
        self,
        user: User,
        user_agent: str,
    ) -> Dict[str, str]:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )

        return await create_and_store_tokens(
            redis=self.redis,
            user_id=user.id,
            user_agent=user_agent,
        )