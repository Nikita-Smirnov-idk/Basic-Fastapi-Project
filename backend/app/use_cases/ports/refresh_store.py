"""Port: refresh token storage (Redis). Implemented in infrastructure/redis."""
from abc import ABC, abstractmethod
from typing import Any


class IRefreshTokenStore(ABC):
    """Abstract interface for refresh token storage and session management."""

    @abstractmethod
    async def store_refresh_token(
        self,
        user_id: str,
        user_agent: str,
        jti: str,
        family_id: str | None = None,
    ) -> str:
        """Store refresh token, return family_id."""
        ...

    @abstractmethod
    async def get_family_data(self, family_id: str) -> dict[str, Any] | None:
        """Get metadata of family by family_id. Returns None if not found."""
        ...

    @abstractmethod
    async def block_family(self, family_id: str, user_id: str) -> None:
        ...

    @abstractmethod
    async def is_family_blocked(self, family_id: str) -> bool:
        ...

    @abstractmethod
    async def get_sessions_by_user_id(self, user_id: str) -> dict[str, Any]:
        """Return dict family_id -> session data."""
        ...
