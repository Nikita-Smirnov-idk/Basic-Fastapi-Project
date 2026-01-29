import logging
from typing import Optional

from fastapi import HTTPException, status

from app.db.postgres.unit_of_work import UnitOfWork
from app.models.general.models import Message
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class PasswordService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def recover_password(self, email: str) -> Message:
        """
        Инициирует процесс восстановления пароля:
        - проверяет существование пользователя
        - генерирует токен
        - отправляет письмо (если emails_enabled)
        """
        async with self.uow as uow:
            user = uow.users.get_by_email(email)
            if not user:
                # Не раскрываем, существует email или нет
                logger.info("Password recovery requested for non-existing email: %s", email)
                return

            if not user.is_active:
                logger.info("Password recovery requested for inactive user: %s", email)
                return

            # Генерируем токен
            reset_token = generate_password_reset_token(email=email)

            # Подготавливаем и отправляем письмо
            if settings.emails_enabled:
                email_data = generate_reset_password_email(
                    email_to=user.email,
                    email=email,
                    token=reset_token,
                )
                send_email(
                    email_to=user.email,
                    subject=email_data.subject,
                    html_content=email_data.html_content,
                )
                logger.info("Password reset email sent to %s", email)
            else:
                logger.info("Emails disabled, skipping password reset email for %s", email)

    async def reset_password(self, token: str, new_password: str) -> Message:
        """
        Сброс пароля по токену из письма
        """
        email = verify_password_reset_token(token=token)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token"
            )

        async with self.uow as uow:
            user = uow.users.get_by_email(email)
            if not user:
                # На случай, если email был удалён после отправки письма
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid password reset request"
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User account is inactive"
                )

            uow.users.change_password(user, new_password)

            await uow.commit()

            logger.info("Password successfully reset for user_id=%s", user.id)