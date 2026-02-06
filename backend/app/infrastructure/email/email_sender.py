"""Implementation of IEmailSender. Uses app.utils for templates and SMTP."""
from app.use_cases.ports.email_sender import IEmailSender
from .interfaces import IEmailService
from .email_service import get_email_service

class EmailSender(IEmailSender):
    def __init__(self, email_service: IEmailService):
        self.email_service = email_service
    def send_signup_confirmation(self, email: str, token: str) -> None:
        email_data = self.email_service.generate_signup_confirmation_email(email=email, token=token)
        self.email_service.send_email(email_to=email, subject=email_data.subject, html_content=email_data.html_content)

    def send_password_reset(self, email_to: str, email: str, token: str) -> None:
        email_data = self.email_service.generate_reset_password_email(email_to=email_to, email=email, token=token)
        self.email_service.send_email(email_to=email_to, subject=email_data.subject, html_content=email_data.html_content)


_email_sender: EmailSender | None = None


def get_email_sender() -> EmailSender:
    global _email_sender
    if _email_sender is None:
        _email_sender = EmailSender(get_email_service())
    return _email_sender
