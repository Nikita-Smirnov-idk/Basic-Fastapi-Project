"""
Password use case: recover, reset.
Depends only on ports (IUnitOfWork, ITokenService, IEmailSender).
Raises domain exceptions; transport maps to HTTP.
"""
import logging

from app.use_cases.ports.email_sender import IEmailSender
from app.use_cases.ports.token_service import ITokenService
from app.use_cases.ports.unit_of_work import IUnitOfWork
from app.domain.exceptions import InvalidCredentialsError

logger = logging.getLogger(__name__)


class PasswordUseCase:
    def __init__(
        self,
        uow: IUnitOfWork,
        token_service: ITokenService,
        email_sender: IEmailSender,
        emails_enabled: bool,
    ):
        self._uow = uow
        self._token_service = token_service
        self._email_sender = email_sender
        self._emails_enabled = emails_enabled

    async def recover_password(self, email: str) -> None:
        async with self._uow as uow:
            user = await uow.users.get_by_email(email)
            if not user:
                logger.info("Password recovery requested for non-existing email: %s", email)
                return
            if not user.is_active:
                logger.info("Password recovery requested for inactive user: %s", email)
                return
            reset_token = self._token_service.create_password_reset_token(email)
            if self._emails_enabled:
                self._email_sender.send_password_reset(
                    email_to=user.email, email=email, token=reset_token
                )
                logger.info("Password reset email sent to %s", email)
            else:
                logger.info("Emails disabled, skipping password reset email for %s", email)

    async def reset_password(self, token: str, new_password: str) -> None:
        email = self._token_service.verify_password_reset_token(token)
        if not email:
            raise InvalidCredentialsError("Invalid or expired password reset token")
        async with self._uow as uow:
            user = await uow.users.get_by_email(email)
            if not user:
                raise InvalidCredentialsError("Invalid password reset request")
            if not user.is_active:
                raise InvalidCredentialsError("User account is inactive")
            uow.users.change_password(user=user, new_password=new_password)
            await uow.commit()
            logger.info("Password reset for user_id=%s", user.id)
