"""Port: user persistence. Implemented in infrastructure/persistence."""
from abc import ABC, abstractmethod
from typing import Any


class IUserRepository(ABC):
    """Abstract interface for user persistence. All return types are Any to avoid depending on DB models."""

    @abstractmethod
    def create_by_password(
        self,
        *,
        email: str,
        password: str,
        full_name: str | None = None,
        is_verified: bool = False,
        is_superuser: bool = False,
    ) -> Any:
        """Create user with hashed password. Returns user (DB or domain)."""
        ...

    @abstractmethod
    def create_by_google(
        self,
        *,
        email: str,
        google_id: str,
        is_verified: bool = True,
        full_name: str | None = None,
    ) -> Any:
        ...

    @abstractmethod
    async def get_by_id(self, user_id: Any) -> Any:
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Any:
        ...

    @abstractmethod
    async def get_by_google_id(self, google_id: str) -> Any:
        ...

    @abstractmethod
    async def authenticate(self, *, email: str, password: str) -> Any:
        """Returns user if credentials valid, else None."""
        ...

    @abstractmethod
    def update(self, *, user: Any, user_in: Any) -> Any:
        ...

    @abstractmethod
    def change_password(self, *, user: Any, new_password: str) -> Any:
        ...

    @abstractmethod
    def link_google_id(self, *, user: Any, google_id: str) -> Any:
        ...

    @abstractmethod
    async def delete(self, user: Any) -> None:
        ...

    @abstractmethod
    async def get_list(self, *, skip: int = 0, limit: int = 100) -> tuple[list[Any], int]:
        """Return (list of users, total count)."""
        ...
