"""Admin stats repository: aggregates dashboard data. Implements IAdminStatsRepository."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.domain.entities.db.user import User
from app.domain.entities.db.yc_company import YCCompany
from app.domain.entities.db.yc_founder import YCFounder
from app.use_cases.ports.admin_stats_repository import (
    AdminDashboardStatsData,
    IAdminStatsRepository,
)


class AdminStatsRepository(IAdminStatsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_dashboard_stats(self) -> AdminDashboardStatsData:
        users_count_stmt = select(func.count()).select_from(User)
        users_result = await self._session.execute(users_count_stmt)
        total_users = int(users_result.scalar_one())

        paying_stmt = select(func.count()).select_from(User).where(User.plan != "free")
        paying_result = await self._session.execute(paying_stmt)
        paying_users = int(paying_result.scalar_one())

        balance_stmt = select(func.coalesce(func.sum(User.balance_cents), 0))
        balance_result = await self._session.execute(balance_stmt)
        total_balance_cents = int(balance_result.scalar_one() or 0)

        yc_stmt = select(func.count()).select_from(YCCompany)
        yc_result = await self._session.execute(yc_stmt)
        yc_companies_count = int(yc_result.scalar_one())

        ycf_stmt = select(func.count()).select_from(YCFounder)
        ycf_result = await self._session.execute(ycf_stmt)
        yc_founders_count = int(ycf_result.scalar_one())

        return AdminDashboardStatsData(
            total_users=total_users,
            paying_users=paying_users,
            total_balance_cents=total_balance_cents,
            yc_companies_count=yc_companies_count,
            yc_founders_count=yc_founders_count,
        )
