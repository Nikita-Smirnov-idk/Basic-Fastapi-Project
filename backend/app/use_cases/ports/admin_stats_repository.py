"""Port: admin dashboard stats aggregation. Implemented in infrastructure."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class AdminDashboardStatsData:
    total_users: int
    paying_users: int
    total_balance_cents: int
    yc_companies_count: int
    yc_founders_count: int


class IAdminStatsRepository(ABC):
    @abstractmethod
    async def get_dashboard_stats(self) -> AdminDashboardStatsData:
        """Return aggregated stats for admin dashboard."""
        ...
