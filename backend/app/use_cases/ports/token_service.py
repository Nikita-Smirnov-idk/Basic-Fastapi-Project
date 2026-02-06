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
    def decode_and_validate(self, token: str, expected_type: str) -> dict[str, Any]:
        """Decode JWT and validate type/iss. Raises ValueError on invalid/expired/wrong-type."""
        ...

    @abstractmethod
    def compare_refresh_payload_and_stored_data(self, payload: dict[str, Any], stored_data: dict[str, Any] | None) -> None:
        """Validate User user_id/jti/family_id. Raises ValueError on invalid/expired/wrong-type."""
        ...

    @abstractmethod
    def get_sub(self, payload: dict[str, Any]) -> str:
        """Extract sub claim. Raises ValueError if missing."""
        ...

    @abstractmethod
    def get_jti(self, payload: dict[str, Any]) -> str:
        """Extract jti. Raises ValueError if missing."""
        ...

    @abstractmethod
    def get_family_id(self, payload: dict[str, Any]) -> str:
        """Extract family_id. Raises ValueError if missing."""
        ...

    @abstractmethod
    def verify_token_and_get_sub(
        self, token: str, expected_type: str, *, or_none: bool = False
    ) -> str | None:
        """Decode, validate type, return sub. Raises ValueError if or_none=False and invalid. Returns None if or_none=True and invalid."""
        ...
