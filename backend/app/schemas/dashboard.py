from decimal import Decimal
from pydantic import BaseModel
from app.schemas.order import OrderResponse

class DashboardSummaryResponse(BaseModel):
    """Schema for dashboard summary statistics."""
    total_orders: int
    pending_orders: int
    processing_orders: int
    completed_orders: int
    cancelled_orders: int
    total_revenue: Decimal

class StatusDistributionResponse(BaseModel):
    """Schema for order status distribution."""
    PENDING: int = 0
    PROCESSING: int = 0
    COMPLETED: int = 0
    CANCELLED: int = 0

class MonthlyStatisticItem(BaseModel):
    """Schema for a single month's statistics."""
    month: str
    orders: int
    revenue: Decimal

class MonthlyStatisticsResponse(BaseModel):
    """Schema for monthly dashboard statistics."""
    items: list[MonthlyStatisticItem]

class DashboardFullResponse(BaseModel):
    """Schema for a complete dashboard payload."""
    summary: DashboardSummaryResponse
    recent_orders: list[OrderResponse]
    status_distribution: StatusDistributionResponse
    monthly_statistics: MonthlyStatisticsResponse
