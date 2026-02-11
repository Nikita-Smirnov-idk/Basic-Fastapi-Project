from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from uuid import UUID

from app.domain.entities.db.yc_company import YCCompany
from app.domain.entities.db.yc_founder import YCFounder
from app.domain.entities.db.yc_sync_state import YCSyncState


@dataclass(frozen=True)
class YCSearchFilters:
    q: str | None = None
    batch: str | None = None
    year: int | None = None
    status: str | None = None
    industry: str | None = None
    is_hiring: bool | None = None
    nonprofit: bool | None = None
    top_company: bool | None = None


class IYCDirectoryRepository(ABC):
    @abstractmethod
    async def get_sync_state(self) -> YCSyncState | None:
        ...

    @abstractmethod
    async def sync_from_source(self) -> int:
        ...

    @abstractmethod
    async def list_companies(
        self,
        filters: YCSearchFilters,
        skip: int,
        limit: int,
    ) -> tuple[list[YCCompany], int]:
        ...

    @abstractmethod
    async def get_founders_for_company_ids(self, company_ids: list[UUID]) -> list[YCFounder]:
        ...

    @abstractmethod
    async def get_meta(self) -> dict[str, Any]:
        ...
