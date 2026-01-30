"""Implementation of IEmailSender. Uses app.utils for templates and SMTP."""
from app.use_cases.ports.email_sender import IEmailSender

# Import here to avoid circular deps; utils are cross-cutting
def _send_signup_confirmation(email: str, token: str) -> None:
    from app.utils import generate_signup_confirmation_email, send_email
    email_data = generate_signup_confirmation_email(email=email, token=token)
    send_email(email_to=email, subject=email_data.subject, html_content=email_data.html_content)


def _send_password_reset(email_to: str, email: str, token: str) -> None:
    from app.utils import generate_reset_password_email, send_email
    email_data = generate_reset_password_email(email_to=email_to, email=email, token=token)
    send_email(email_to=email_to, subject=email_data.subject, html_content=email_data.html_content)


class EmailSender(IEmailSender):
    def send_signup_confirmation(self, email: str, token: str) -> None:
        _send_signup_confirmation(email=email, token=token)

    def send_password_reset(self, email_to: str, email: str, token: str) -> None:
        _send_password_reset(email_to=email_to, email=email, token=token)


_email_sender: EmailSender | None = None


def get_email_sender() -> EmailSender:
    global _email_sender
    if _email_sender is None:
        _email_sender = EmailSender()
    return _email_sender
