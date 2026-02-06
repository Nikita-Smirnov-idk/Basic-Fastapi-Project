"""
Single implementation of all JWT logic (access, refresh, signup, password-reset, decode).
Implements ITokenService. Used by use cases and API deps.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.use_cases.ports.token_service import ITokenService
from app.core.config.config import settings

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"


class TokenService(ITokenService):
    """All token operations in one place: create, decode, validate."""

    def __init__(
        self,
        *,
        secret_key: str = settings.SECRET_KEY,
        issuer: str = settings.FRONTEND_HOST,
        access_expire_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_expire_days: int = settings.REFRESH_TOKEN_EXPIRE_DAYS,
        signup_expire_minutes: int = settings.SIGNUP_TOKEN_EXPIRE_MINUTES,
        password_reset_expire_hours: int = settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
    ):
        self._secret_key = secret_key
        self._issuer = issuer
        self._access_expire_minutes = access_expire_minutes
        self._refresh_expire_days = refresh_expire_days
        self._signup_expire_minutes = signup_expire_minutes
        self._password_reset_expire_hours = password_reset_expire_hours

    def _create_typed_token(
        self,
        data: dict[str, Any],
        token_type: str,
        exp_delta: timedelta,
        *,
        nbf: bool = False,
    ) -> str:
        """Common logic: add exp, type, iss to payload and encode."""
        now = datetime.now(timezone.utc)
        expire = now + exp_delta
        to_encode = {
            **data,
            "exp": expire,
            "type": token_type,
            "iss": self._issuer,
        }
        if nbf:
            to_encode["nbf"] = now.timestamp()
        return jwt.encode(to_encode, self._secret_key, algorithm=ALGORITHM)

    def create_access_token(self, data: dict[str, Any]) -> str:
        return self._create_typed_token(
            data,
            "access",
            timedelta(minutes=self._access_expire_minutes),
        )

    def create_refresh_token(self, data: dict[str, Any]) -> str:
        return self._create_typed_token(
            data,
            "refresh",
            timedelta(days=self._refresh_expire_days),
        )

    def create_signup_token(self, data: dict[str, Any]) -> str:
        return self._create_typed_token(
            data,
            "signup",
            timedelta(minutes=self._signup_expire_minutes),
        )

    def create_password_reset_token(self, email: str) -> str:
        return self._create_typed_token(
            {"sub": email},
            "password_reset",
            timedelta(hours=self._password_reset_expire_hours),
            nbf=True,
        )

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, self._secret_key, algorithms=[ALGORITHM])
        except ExpiredSignatureError:
            logger.debug("Token expired")
            raise ValueError("Token expired") from None
        except InvalidTokenError:
            logger.debug("Invalid token")
            raise ValueError("Invalid token") from None

    def _validate_type_and_issuer(self, payload: dict[str, Any], expected_type: str) -> None:
        """Validate token type and issuer. Raises ValueError if invalid."""
        if payload.get("type") != expected_type:
            raise ValueError(f"Invalid token payload: expected type {expected_type}")
        if payload.get("iss") != self._issuer:
            raise ValueError("Invalid token payload")

    def decode_and_validate(self, token: str, expected_type: str) -> dict[str, Any]:
        """Decode JWT and validate type/iss. Raises ValueError on invalid/expired/wrong-type."""
        payload = self.decode_token(token)
        self._validate_type_and_issuer(payload, expected_type)
        return payload

    def get_sub(self, payload: dict[str, Any]) -> str:
        """Extract sub claim. Raises ValueError if missing."""
        sub = payload.get("sub")
        if sub is None:
            raise ValueError("Invalid token payload")
        return str(sub)

    def verify_token_and_get_sub(
        self, token: str, expected_type: str, *, or_none: bool = False
    ) -> str | None:
        """Decode, validate type, return sub. Raises ValueError if or_none=False and invalid."""
        try:
            payload = self.decode_and_validate(token, expected_type)
            return self.get_sub(payload)
        except ValueError:
            if or_none:
                return None
            raise


# Default instance for dependency injection
_token_service: TokenService | None = None


def get_token_service() -> TokenService:
    global _token_service
    if _token_service is None:
        _token_service = TokenService()
    return _token_service
