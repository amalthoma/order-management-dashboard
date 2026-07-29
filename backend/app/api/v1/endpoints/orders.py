import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdateStatus
from app.schemas.order_filter import OrderFilter
from app.schemas.pagination import PaginatedResponse
from app.services.order_service import OrderService
from app.models.user import User
from app.utils.responses import StandardResponse

router = APIRouter()

@router.post(
    "/",
    response_model=StandardResponse[OrderResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Order"
)
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new order."""
    order_service = OrderService(db)
    order = await order_service.create_order(order_in, current_user.id)
    return StandardResponse(
        data=order,
        message="Order created successfully"
    )

@router.get(
    "/",
    response_model=StandardResponse[PaginatedResponse[OrderResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Orders"
)
async def list_orders(
    filters: OrderFilter = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List orders with filtering, sorting, and pagination."""
    order_service = OrderService(db)
    paginated_orders = await order_service.list_orders_filtered(filters)
    return StandardResponse(
        data=paginated_orders,
        message="Orders retrieved successfully"
    )

@router.get(
    "/{order_id}",
    response_model=StandardResponse[OrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Order Details"
)
async def get_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve details of a specific order."""
    order_service = OrderService(db)
    order = await order_service.get_order(order_id)
    return StandardResponse(
        data=order,
        message="Order retrieved successfully"
    )

@router.patch(
    "/{order_id}/status",
    response_model=StandardResponse[OrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Status"
)
async def update_status(
    order_id: uuid.UUID,
    update_data: OrderUpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the status of an order."""
    order_service = OrderService(db)
    order = await order_service.update_order_status(order_id, update_data)
    return StandardResponse(
        data=order,
        message="Order status updated successfully"
    )
