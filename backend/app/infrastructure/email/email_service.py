import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import emails  # type: ignore
from jinja2 import Template

from app.infrastructure.jwt.token_service import get_token_service
from pydantic import EmailStr
from app.core.config.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailData:
    html_content: str
    subject: str

class EmailService:
    def __init__(
            self,
            *,
            emails_enabled: bool = settings.emails_enabled,
            email_from_name: str = settings.EMAILS_FROM_NAME,
            emails_from_email: EmailStr = settings.EMAILS_FROM_EMAIL,
            smtp_host: str = settings.SMTP_HOST,
            smtp_port: int = settings.SMTP_PORT,
            smtp_tls: bool = settings.SMTP_TLS,
            smtp_ssl: bool = settings.SMTP_SSL,
            smtp_user: str = settings.SMTP_USER,
            smtp_password: str = settings.SMTP_PASSWORD,
            project_name: str = settings.PROJECT_NAME,
            frontend_host: str = settings.FRONTEND_HOST,
            email_reset_token_expire_hours: int = settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            signup_token_expire_minutes: int = settings.SIGNUP_TOKEN_EXPIRE_MINUTES,
        ):
        self.emails_enabled = emails_enabled
        self.email_from_name = email_from_name
        self.emails_from_email = emails_from_email
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_tls = smtp_tls
        self.smtp_ssl = smtp_ssl
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.project_name = project_name
        self.frontend_host = frontend_host
        self.email_reset_token_expire_hours = email_reset_token_expire_hours
        self.signup_token_expire_minutes = signup_token_expire_minutes

    def render_email_template(self, *, template_name: str, context: dict[str, Any]) -> str:
        template_str = (
            Path(__file__).parent / "email-templates" / "build" / template_name
        ).read_text()
        html_content = Template(template_str).render(context)
        return html_content


    def send_email(
        self,
        *,
        email_to: str,
        subject: str = "",
        html_content: str = "",
    ) -> None:
        assert self.emails_enabled, "no provided configuration for email variables"
        message = emails.Message(
            subject=subject,
            html=html_content,
            mail_from=(self.email_from_name, self.emails_from_email),
        )
        smtp_options = {"host": self.smtp_host, "port": self.smtp_port}
        if self.smtp_tls:
            smtp_options["tls"] = True
        elif self.smtp_ssl:
            smtp_options["ssl"] = True
        if self.smtp_user:
            smtp_options["user"] = self.smtp_user
        if self.smtp_password:
            smtp_options["password"] = self.smtp_password
        response = message.send(to=email_to, smtp=smtp_options)
        logger.info(f"send email result: {response}")


    def generate_test_email(self, email_to: str) -> EmailData:
        project_name = self.project_name
        subject = f"{project_name} - Test email"
        html_content = self.render_email_template(
            template_name="test_email.html",
            context={"project_name": self.project_name, "email": email_to},
        )
        return EmailData(html_content=html_content, subject=subject)


    def generate_reset_password_email(self, *, email_to: str, email: str, token: str) -> EmailData:
        project_name = self.project_name
        subject = f"{project_name} - Password recovery for user {email}"
        link = f"{self.frontend_host}/reset-password?token={token}"
        html_content = self.render_email_template(
            template_name="reset_password.html",
            context={
                "project_name": self.project_name,
                "username": email,
                "email": email_to,
                "valid_hours": self.email_reset_token_expire_hours,
                "link": link,
            },
        )
        return EmailData(html_content=html_content, subject=subject)


    def generate_new_account_email(
        self, *, email_to: str, username: str, password: str
    ) -> EmailData:
        project_name = self.project_name
        subject = f"{project_name} - New account for user {username}"
        html_content = self.render_email_template(
            template_name="new_account.html",
            context={
                "project_name": self.project_name,
                "username": username,
                "password": password,
                "email": email_to,
                "link": self.frontend_host,
            },
        )
        return EmailData(html_content=html_content, subject=subject)


    def generate_signup_confirmation_email(self, *, email: str, token: str) -> EmailData:
        """Генерирует email для подтверждения регистрации"""
        project_name = self.project_name
        subject = f"{project_name} - Подтвердите регистрацию"
        link = f"{self.frontend_host}/verify?token={token}"
        html_content = self.render_email_template(
            template_name="signup_confirmation.html",
            context={
                "project_name": project_name,
                "email": email,
                "link": link,
                "valid_minutes": self.signup_token_expire_minutes,
            },
        )
        return EmailData(html_content=html_content, subject=subject)


_email_service: EmailService | None = None

def get_email_service() -> EmailService:
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
