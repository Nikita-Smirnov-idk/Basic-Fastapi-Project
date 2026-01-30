"""Port: refresh token storage (Redis). Implemented in infrastructure/redis."""
from abc import ABC, abstractmethod
from typing import Any


class IRefreshTokenStore(ABC):
    """Abstract interface for refresh token storage and session management."""

    @abstractmethod
    async def store_refresh_token(
        self,
        user_id: str,
        refresh_token: str,
        user_agent: str,
        family_id: str | None = None,
    ) -> str:
        """Store refresh token, return family_id."""
        ...

    @abstractmethod
    async def get_refresh_data(self, refresh_token: str) -> dict[str, Any] | None:
        """Get metadata by refresh token. Returns None if not found."""
        ...

    @abstractmethod
    async def block_refresh(self, token: str) -> None:
        ...

    @abstractmethod
    async def is_refresh_blocked(self, token: str) -> bool:
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
