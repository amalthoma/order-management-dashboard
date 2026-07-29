import uuid
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field
from app.core.enums import OrderStatus

class OrderBase(BaseModel):
    """Base schema for order data."""
    customer_name: str = Field(..., max_length=150)
    amount: Decimal = Field(..., gt=0, description="Amount must be greater than zero.")

class OrderCreate(OrderBase):
    """Schema for creating a new order."""
    pass

class OrderUpdateStatus(BaseModel):
    """Schema for updating order status."""
    status: OrderStatus

class OrderResponse(OrderBase):
    """Schema for returning order data."""
    id: uuid.UUID
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID

    model_config = {"from_attributes": True}
