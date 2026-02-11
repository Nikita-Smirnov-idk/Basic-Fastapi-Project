from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from uuid import UUID

from app.domain.entities.db.yc_company import YCCompany
from app.domain.entities.db.yc_founder import YCFounder
from app.domain.entities.db.yc_sync_state import YCSyncState
from app.use_cases.ports.yc_directory_repository import (
    IYCDirectoryRepository,
    YCSearchFilters,
)


class YCDirectoryUseCase:
    def __init__(
        self,
        repo: IYCDirectoryRepository,
        auto_sync_interval: timedelta,
    ) -> None:
        self._repo = repo
        self._auto_sync_interval = auto_sync_interval

    async def ensure_auto_sync(self) -> None:
        now = datetime.utcnow()
        state = await self._repo.get_sync_state()
        if not state or not state.last_success_at:
            await self._repo.sync_from_source()
            return
        if now - state.last_success_at >= self._auto_sync_interval:
            await self._repo.sync_from_source()

    async def sync_from_source(self) -> int:
        return await self._repo.sync_from_source()

    async def list_companies(
        self,
        filters: YCSearchFilters,
        skip: int,
        limit: int,
    ) -> tuple[list[YCCompany], int]:
        return await self._repo.list_companies(filters=filters, skip=skip, limit=limit)

    async def get_founders_for_company_ids(self, company_ids: list[UUID]) -> list[YCFounder]:
        return await self._repo.get_founders_for_company_ids(company_ids)

    async def get_meta(self) -> dict[str, Any]:
        return await self._repo.get_meta()

    async def get_sync_state(self) -> YCSyncState | None:
        return await self._repo.get_sync_state()
