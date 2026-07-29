import logging
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    StatusDistributionResponse,
    MonthlyStatisticItem,
    MonthlyStatisticsResponse,
    DashboardFullResponse
)
from app.schemas.order import OrderResponse

logger = logging.getLogger(__name__)

class DashboardService:
    """Service layer for dashboard analytics management."""

    def __init__(self, session: AsyncSession):
        """
        Initializes the DashboardService.

        Args:
            session (AsyncSession): The database session.
        """
        self.session = session
        self.dashboard_repo = DashboardRepository(session)

    async def get_dashboard_summary(self) -> DashboardSummaryResponse:
        """
        Retrieves the overall dashboard summary statistics.

        Returns:
            DashboardSummaryResponse: The aggregated dashboard summary.
        """
        data = await self.dashboard_repo.get_dashboard_summary()
        logger.info("Dashboard summary loaded.")
        return DashboardSummaryResponse(**data)

    async def get_recent_orders(self, limit: int = 10) -> list[OrderResponse]:
        """
        Retrieves the most recent orders.

        Args:
            limit (int): The maximum number of orders to return. Defaults to 10.

        Returns:
            list[OrderResponse]: A list of recent orders.
        """
        orders = await self.dashboard_repo.get_recent_orders(limit)
        logger.info("Recent orders loaded.")
        return [OrderResponse.model_validate(order) for order in orders]

    async def get_status_distribution(self) -> StatusDistributionResponse:
        """
        Retrieves the distribution of orders by status.

        Returns:
            StatusDistributionResponse: The counts of orders grouped by status.
        """
        data = await self.dashboard_repo.get_status_distribution()
        logger.info("Status distribution loaded.")
        return StatusDistributionResponse(**data)

    async def get_monthly_statistics(self) -> MonthlyStatisticsResponse:
        """
        Retrieves aggregated order counts and revenue by month.

        Returns:
            MonthlyStatisticsResponse: A wrapped list of monthly statistics.
        """
        data = await self.dashboard_repo.get_monthly_statistics()
        items = [MonthlyStatisticItem(**item) for item in data]
        logger.info("Monthly statistics loaded.")
        return MonthlyStatisticsResponse(items=items)

    async def get_full_dashboard(self, recent_orders_limit: int = 10) -> DashboardFullResponse:
        """
        Retrieves the complete dashboard payload concurrently.

        Returns:
            DashboardFullResponse: An aggregated payload of all dashboard statistics.
        """
        summary, recent_orders, status_distribution, monthly_statistics = await asyncio.gather(
            self.get_dashboard_summary(),
            self.get_recent_orders(limit=recent_orders_limit),
            self.get_status_distribution(),
            self.get_monthly_statistics()
        )
        
        logger.info("Complete dashboard payload loaded.")
        return DashboardFullResponse(
            summary=summary,
            recent_orders=recent_orders,
            status_distribution=status_distribution,
            monthly_statistics=monthly_statistics
        )
