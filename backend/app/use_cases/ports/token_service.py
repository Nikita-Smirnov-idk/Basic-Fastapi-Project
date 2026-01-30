"""Port: token creation and validation. Implemented in infrastructure/jwt."""
from abc import ABC, abstractmethod
from typing import Any


class ITokenService(ABC):
    """Abstract interface for JWT: access, refresh, signup, decode, password-reset."""

    @abstractmethod
    def create_access_token(self, data: dict[str, Any]) -> str:
        ...

    @abstractmethod
    def create_refresh_token(self, data: dict[str, Any]) -> str:
        ...

    @abstractmethod
    def create_signup_token(self, data: dict[str, Any]) -> str:
        ...

    @abstractmethod
    def create_password_reset_token(self, email: str) -> str:
        ...

    @abstractmethod
    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and validate JWT. Raises ValueError on invalid/expired."""
        ...

    @abstractmethod
    def verify_password_reset_token(self, token: str) -> str | None:
        """Returns email (sub) or None if invalid/expired."""
        ...

    @abstractmethod
    def validate_access_payload(self, payload: dict[str, Any]) -> str:
        """Validate access token payload (type, iss). Returns sub (user_id). Raises ValueError."""
        ...

    @abstractmethod
    def validate_payload_type(self, payload: dict[str, Any], expected_type: str) -> None:
        """Validate token type and issuer. Raises ValueError if invalid."""
        ...
