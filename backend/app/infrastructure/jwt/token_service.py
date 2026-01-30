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
from app.config import settings

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

    def create_access_token(self, data: dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._access_expire_minutes)
        to_encode.update({"exp": expire, "type": "access", "iss": self._issuer})
        return jwt.encode(to_encode, self._secret_key, algorithm=ALGORITHM)

    def create_refresh_token(self, data: dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=self._refresh_expire_days)
        to_encode.update({"exp": expire, "type": "refresh", "iss": self._issuer})
        return jwt.encode(to_encode, self._secret_key, algorithm=ALGORITHM)

    def create_signup_token(self, data: dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._signup_expire_minutes)
        to_encode.update({"exp": expire, "type": "signup", "iss": self._issuer})
        return jwt.encode(to_encode, self._secret_key, algorithm=ALGORITHM)

    def create_password_reset_token(self, email: str) -> str:
        delta = timedelta(hours=self._password_reset_expire_hours)
        now = datetime.now(timezone.utc)
        expires = now + delta
        exp = expires.timestamp()
        return jwt.encode(
            {"exp": exp, "nbf": now.timestamp(), "sub": email},
            self._secret_key,
            algorithm=ALGORITHM,
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

    def verify_password_reset_token(self, token: str) -> str | None:
        try:
            decoded = jwt.decode(token, self._secret_key, algorithms=[ALGORITHM])
            return str(decoded["sub"])
        except (InvalidTokenError, KeyError):
            return None

    def validate_access_payload(self, payload: dict[str, Any]) -> str:
        self.validate_payload_type(payload, "access")
        sub = payload.get("sub")
        if sub is None:
            raise ValueError("Invalid token payload")
        return str(sub)

    def validate_payload_type(self, payload: dict[str, Any], expected_type: str) -> None:
        """Validate token type and issuer. Raises ValueError if invalid."""
        if payload.get("type") != expected_type:
            raise ValueError(f"Invalid token payload: expected type {expected_type}")
        if payload.get("iss") != self._issuer:
            raise ValueError("Invalid token payload")


# Default instance for dependency injection
_token_service: TokenService | None = None


def get_token_service() -> TokenService:
    global _token_service
    if _token_service is None:
        _token_service = TokenService()
    return _token_service
