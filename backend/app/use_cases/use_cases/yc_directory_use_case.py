from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.config import settings
from app.domain.entities.db.yc_company import YCCompany
from app.domain.entities.db.yc_sync_state import YCSyncState
from app.infrastructure.yc.sync import sync_yc_directory


AUTO_SYNC_INTERVAL = timedelta(days=settings.YC_AUTO_SYNC_DAYS)


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


class YCDirectoryUseCase:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def ensure_auto_sync(self) -> None:
        """Trigger sync if last successful sync was more than AUTO_SYNC_INTERVAL ago.

        This is a lazy scheduler: the check runs when YC data is accessed.
        """
        now = datetime.utcnow()
        state = await self.get_sync_state()

        # No previous sync state -> perform initial sync
        if not state or not state.last_success_at:
            await self.sync_from_source()
            return

        if now - state.last_success_at >= AUTO_SYNC_INTERVAL:
            await self.sync_from_source()

    async def sync_from_source(self) -> int:
        """Delegate full YC sync to infrastructure layer."""
        return await sync_yc_directory(self._session)

    async def list_companies(
        self,
        filters: YCSearchFilters,
        skip: int,
        limit: int,
    ) -> tuple[list[YCCompany], int]:
        stmt = select(YCCompany)
        count_stmt = select(func.count()).select_from(YCCompany)

        stmt, count_stmt = self._apply_filters(stmt, count_stmt, filters)

        stmt = stmt.order_by(YCCompany.batch_code.desc(), YCCompany.name.asc()).offset(skip).limit(
            limit
        )

        result = await self._session.execute(stmt)
        items = result.scalars().all()

        count_result = await self._session.execute(count_stmt)
        count = count_result.scalar_one()

        return items, int(count)

    async def get_meta(self) -> dict[str, Any]:
        years_stmt = select(func.distinct(YCCompany.year)).order_by(YCCompany.year)
        batches_stmt = select(func.distinct(YCCompany.batch)).order_by(YCCompany.batch)
        statuses_stmt = select(func.distinct(YCCompany.status)).order_by(YCCompany.status)
        industries_stmt = select(func.distinct(YCCompany.industry)).where(
            YCCompany.industry.is_not(None),
        )

        years = [row[0] for row in (await self._session.execute(years_stmt)).all() if row[0]]
        batches = [row[0] for row in (await self._session.execute(batches_stmt)).all() if row[0]]
        statuses = [
            row[0] for row in (await self._session.execute(statuses_stmt)).all() if row[0]
        ]
        industries = [
            row[0] for row in (await self._session.execute(industries_stmt)).all() if row[0]
        ]

        return {
            "years": years,
            "batches": batches,
            "statuses": statuses,
            "industries": industries,
        }

    async def get_sync_state(self) -> YCSyncState | None:
        stmt = select(YCSyncState).where(YCSyncState.source == "yc_directory")
        result = await self._session.execute(stmt)
        return result.scalars().first()

    def _apply_filters(self, stmt, count_stmt, filters: YCSearchFilters):
        if filters.q:
            pattern = f"%{filters.q.lower()}%"
            stmt = stmt.where(
                func.lower(YCCompany.name).like(pattern)
                | func.lower(YCCompany.one_liner).like(pattern)
                | func.lower(YCCompany.long_description).like(pattern)
            )
            count_stmt = count_stmt.where(
                func.lower(YCCompany.name).like(pattern)
                | func.lower(YCCompany.one_liner).like(pattern)
                | func.lower(YCCompany.long_description).like(pattern)
            )

        if filters.batch:
            stmt = stmt.where(YCCompany.batch == filters.batch)
            count_stmt = count_stmt.where(YCCompany.batch == filters.batch)
        if filters.year:
            stmt = stmt.where(YCCompany.year == filters.year)
            count_stmt = count_stmt.where(YCCompany.year == filters.year)
        if filters.status:
            stmt = stmt.where(YCCompany.status == filters.status)
            count_stmt = count_stmt.where(YCCompany.status == filters.status)
        if filters.industry:
            stmt = stmt.where(YCCompany.industry == filters.industry)
            count_stmt = count_stmt.where(YCCompany.industry == filters.industry)
        if filters.is_hiring is not None:
            stmt = stmt.where(YCCompany.is_hiring.is_(filters.is_hiring))
            count_stmt = count_stmt.where(YCCompany.is_hiring.is_(filters.is_hiring))
        if filters.nonprofit is not None:
            stmt = stmt.where(YCCompany.nonprofit.is_(filters.nonprofit))
            count_stmt = count_stmt.where(YCCompany.nonprofit.is_(filters.nonprofit))
        if filters.top_company is not None:
            stmt = stmt.where(YCCompany.top_company.is_(filters.top_company))
            count_stmt = count_stmt.where(YCCompany.top_company.is_(filters.top_company))

        return stmt, count_stmt

    def _batch_code(self, batch: str | None) -> str:
        if not batch:
            return ""
        parts = batch.split()
        if len(parts) != 2:
            return ""
        season, year_str = parts
        short = "W" if season.lower().startswith("winter") else "S"
        try:
            year = int(year_str)
        except ValueError:
            return ""
        return f"{short}{year}"

    def _batch_year(self, batch: str | None) -> int:
        if not batch:
            return 0
        parts = batch.split()
        if len(parts) != 2:
            return 0
        try:
            return int(parts[1])
        except ValueError:
            return 0

