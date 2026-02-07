"""Port: email sending. Implemented in infrastructure/email."""
from abc import ABC, abstractmethod


class IEmailSender(ABC):
    """Abstract interface for sending emails (signup, password reset)."""

    @abstractmethod
    def send_signup_confirmation(self, email: str, token: str) -> None:
        """Send signup confirmation email with link."""
        ...

    @abstractmethod
    def send_password_reset(self, email_to: str, email: str, token: str) -> None:
        """Send password reset email with link."""
        ...
