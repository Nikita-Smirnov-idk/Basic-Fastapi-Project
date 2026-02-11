from __future__ import annotations

import asyncio
from uuid import UUID
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer

from app.domain.entities.db.yc_company import YCCompany
from app.domain.entities.db.yc_founder import YCFounder
from app.domain.entities.db.yc_sync_state import YCSyncState
from app.infrastructure.yc.sync import sync_yc_directory
from app.use_cases.ports.yc_directory_repository import IYCDirectoryRepository, YCSearchFilters


class YCDirectoryRepository(IYCDirectoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_sync_state(self) -> YCSyncState | None:
        stmt = select(YCSyncState).where(YCSyncState.source == "yc_directory")
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def sync_from_source(self) -> int:
        return await sync_yc_directory(self._session)

    async def list_companies(
        self,
        filters: YCSearchFilters,
        skip: int,
        limit: int,
    ) -> tuple[list[YCCompany], int]:
        stmt = select(YCCompany, func.count().over().label("_total")).options(
            defer(YCCompany.long_description)
        )
        stmt, _ = _apply_filters(stmt, None, filters)
        stmt = stmt.order_by(YCCompany.batch_code.desc(), YCCompany.name.asc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        rows = result.all()
        items = [row[0] for row in rows]
        total = int(rows[0][1]) if rows else 0
        return items, total

    async def get_founders_for_company_ids(
        self, company_ids: list[UUID]
    ) -> list[YCFounder]:
        if not company_ids:
            return []
        stmt = (
            select(YCFounder)
            .where(YCFounder.company_id.in_(company_ids))
            .order_by(YCFounder.company_id, YCFounder.sort_order)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_meta(self) -> dict[str, Any]:
        years_stmt = select(func.distinct(YCCompany.year)).order_by(YCCompany.year)
        batches_stmt = select(func.distinct(YCCompany.batch)).order_by(YCCompany.batch)
        statuses_stmt = select(func.distinct(YCCompany.status)).order_by(YCCompany.status)
        industries_stmt = select(func.distinct(YCCompany.industry)).where(
            YCCompany.industry.is_not(None),
        )
        r_years, r_batches, r_statuses, r_industries = await asyncio.gather(
            self._session.execute(years_stmt),
            self._session.execute(batches_stmt),
            self._session.execute(statuses_stmt),
            self._session.execute(industries_stmt),
        )
        years = [row[0] for row in r_years.all() if row[0]]
        batches = [row[0] for row in r_batches.all() if row[0]]
        statuses = [row[0] for row in r_statuses.all() if row[0]]
        industries = [row[0] for row in r_industries.all() if row[0]]
        return {
            "years": years,
            "batches": batches,
            "statuses": statuses,
            "industries": industries,
        }


def _apply_filters(stmt, count_stmt, filters: YCSearchFilters):
    if filters.q:
        pattern = f"%{filters.q.lower()}%"
        cond = (
            func.lower(YCCompany.name).like(pattern)
            | func.lower(YCCompany.one_liner).like(pattern)
            | func.lower(YCCompany.long_description).like(pattern)
        )
        stmt = stmt.where(cond)
        if count_stmt is not None:
            count_stmt = count_stmt.where(cond)
    if filters.batch:
        stmt = stmt.where(YCCompany.batch == filters.batch)
        if count_stmt is not None:
            count_stmt = count_stmt.where(YCCompany.batch == filters.batch)
    if filters.year:
        stmt = stmt.where(YCCompany.year == filters.year)
        if count_stmt is not None:
            count_stmt = count_stmt.where(YCCompany.year == filters.year)
    if filters.status:
        stmt = stmt.where(YCCompany.status == filters.status)
        if count_stmt is not None:
            count_stmt = count_stmt.where(YCCompany.status == filters.status)
    if filters.industry:
        stmt = stmt.where(YCCompany.industry == filters.industry)
        if count_stmt is not None:
            count_stmt = count_stmt.where(YCCompany.industry == filters.industry)
    if filters.is_hiring is not None:
        stmt = stmt.where(YCCompany.is_hiring.is_(filters.is_hiring))
        if count_stmt is not None:
            count_stmt = count_stmt.where(YCCompany.is_hiring.is_(filters.is_hiring))
    if filters.nonprofit is not None:
        stmt = stmt.where(YCCompany.nonprofit.is_(filters.nonprofit))
        if count_stmt is not None:
            count_stmt = count_stmt.where(YCCompany.nonprofit.is_(filters.nonprofit))
    if filters.top_company is not None:
        stmt = stmt.where(YCCompany.top_company.is_(filters.top_company))
        if count_stmt is not None:
            count_stmt = count_stmt.where(YCCompany.top_company.is_(filters.top_company))
    return stmt, count_stmt
