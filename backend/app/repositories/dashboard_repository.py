from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order
from app.core.enums import OrderStatus

class DashboardRepository:
    """Repository for fetching dashboard analytics data."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_dashboard_summary(self) -> dict:
        """Retrieves overall summary statistics."""
        stmt = select(
            func.count(Order.id).label("total_orders"),
            func.count(Order.id).filter(Order.status == OrderStatus.PENDING).label("pending"),
            func.count(Order.id).filter(Order.status == OrderStatus.PROCESSING).label("processing"),
            func.count(Order.id).filter(Order.status == OrderStatus.COMPLETED).label("completed"),
            func.count(Order.id).filter(Order.status == OrderStatus.CANCELLED).label("cancelled"),
            func.sum(Order.amount).label("total_revenue")
        )
        result = await self.session.execute(stmt)
        row = result.first()
        
        if not row:
            return {
                "total_orders": 0,
                "pending_orders": 0,
                "processing_orders": 0,
                "completed_orders": 0,
                "cancelled_orders": 0,
                "total_revenue": Decimal("0.00")
            }
            
        return {
            "total_orders": row.total_orders or 0,
            "pending_orders": row.pending or 0,
            "processing_orders": row.processing or 0,
            "completed_orders": row.completed or 0,
            "cancelled_orders": row.cancelled or 0,
            "total_revenue": row.total_revenue or Decimal("0.00")
        }

    async def get_recent_orders(self, limit: int = 10) -> list[Order]:
        """Retrieves the most recent orders."""
        stmt = select(Order).order_by(Order.created_at.desc(), Order.id.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_status_distribution(self) -> dict:
        """Retrieves the count of orders grouped by status."""
        stmt = select(Order.status, func.count(Order.id)).group_by(Order.status)
        result = await self.session.execute(stmt)
        
        distribution = {status.value: 0 for status in OrderStatus}
        for status, count in result.all():
            distribution[status.value] = count
            
        return distribution

    async def get_monthly_statistics(self) -> list[dict]:
        """Retrieves aggregated order counts and revenue by month."""
        month_trunc = func.date_trunc('month', Order.created_at).label('month')
        stmt = select(
            month_trunc,
            func.count(Order.id).label('orders_count'),
            func.sum(Order.amount).label('total_revenue')
        ).group_by(month_trunc).order_by(month_trunc)
        
        result = await self.session.execute(stmt)
        
        stats = []
        for row in result.all():
            if row.month:
                stats.append({
                    "month": row.month.strftime("%Y-%m"),
                    "orders": row.orders_count or 0,
                    "revenue": row.total_revenue or Decimal("0.00")
                })
        return stats
