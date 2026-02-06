# app/infrastructure/email/contracts.py
from abc import ABC, abstractmethod
from typing import Any
from pydantic import EmailStr
from .email_service import EmailData


class IEmailService(ABC):
    @abstractmethod
    def render_email_template(
        self,
        *,
        template_name: str,
        context: dict[str, Any],
    ) -> str:
        """Рендерит HTML из шаблона"""

    @abstractmethod
    def send_email(
        self,
        *,
        email_to: EmailStr,
        subject: str = "",
        html_content: str = "",
    ) -> None:
        """Отправляет email"""

    @abstractmethod
    def generate_test_email(self, email_to: EmailStr) -> EmailData:
        """Генератор тестового письма"""

    @abstractmethod
    def generate_reset_password_email(
        self,
        *,
        email_to: EmailStr,
        email: str,
        token: str,
    ) -> EmailData:
        """Генератор письма для сброса пароля"""

    @abstractmethod
    def generate_new_account_email(
        self,
        *,
        email_to: EmailStr,
        username: str,
        password: str,
    ) -> EmailData:
        """Генератор письма для нового пользователя"""

    @abstractmethod
    def generate_signup_confirmation_email(
        self,
        *,
        email: EmailStr,
        token: str,
    ) -> EmailData:
        """Генератор письма для подтверждения регистрации"""
