from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, Field
from app.core.enums import OrderStatus

class OrderFilter(BaseModel):
    """Schema for filtering, sorting, and paginating orders."""
    search: Optional[str] = Field(None, description="Search by customer name", examples=["John"])
    status: Optional[OrderStatus] = Field(None, description="Filter by exact order status", examples=["PENDING"])
    start_date: Optional[date] = Field(None, description="Start date for order creation (YYYY-MM-DD)", examples=["2026-07-01"])
    end_date: Optional[date] = Field(None, description="End date for order creation (YYYY-MM-DD)", examples=["2026-07-31"])
    sort_by: Literal["created_at", "customer_name", "amount", "status"] = Field(
        "created_at", description="Field to sort by", examples=["created_at"]
    )
    sort_order: Literal["asc", "desc"] = Field("desc", description="Sort direction", examples=["desc"])
    page: int = Field(1, ge=1, description="Page number, starts at 1", examples=[1])
    page_size: int = Field(10, ge=1, le=100, description="Number of items per page", examples=[10])
