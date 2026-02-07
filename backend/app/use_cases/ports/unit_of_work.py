"""Port: unit of work for transactional operations. Implemented in infrastructure."""
from abc import ABC, abstractmethod
from typing import Any

from app.use_cases.ports.user_repository import IUserRepository


class IUnitOfWork(ABC):
    """Abstract unit of work: provides repositories and commit/rollback."""
    
    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        ...

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        ...

    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...
