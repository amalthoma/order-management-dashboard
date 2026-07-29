import uuid
import logging
from math import ceil
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdateStatus
from app.schemas.order_filter import OrderFilter
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.models.order import Order
from app.core.enums import OrderStatus
from app.websocket.manager import manager
from app.websocket.events import ORDER_STATUS_UPDATED

logger = logging.getLogger(__name__)

class OrderService:
    """Service layer for order management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_repo = OrderRepository(session)

    async def create_order(self, order_in: OrderCreate, user_id: uuid.UUID) -> OrderResponse:
        """Creates a new order."""
        if order_in.amount <= 0:
            logger.warning(f"Failed to create order for {user_id}: Amount must be positive.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than zero."
            )
        
        new_order = await self.order_repo.create_order(order_in, user_id)
        await self.session.commit()
        logger.info(f"Order {new_order.id} created successfully by user {user_id}.")
        return OrderResponse.model_validate(new_order)

    async def get_order(self, order_id: uuid.UUID) -> OrderResponse:
        """Retrieves an order by its ID."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            logger.warning(f"Failed to retrieve order: {order_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found."
            )
        logger.info(f"Order {order_id} retrieved successfully.")
        return OrderResponse.model_validate(order)

    async def list_orders(self) -> list[OrderResponse]:
        """Lists all orders."""
        orders = await self.order_repo.list_orders()
        logger.info(f"Retrieved {len(orders)} orders.")
        return [OrderResponse.model_validate(order) for order in orders]

    async def list_orders_filtered(self, filters: OrderFilter) -> PaginatedResponse[OrderResponse]:
        """Lists orders with filtering, sorting, and pagination."""
        orders, total_records = await self.order_repo.list_orders_filtered(filters)
        
        total_pages = ceil(total_records / filters.page_size) if total_records > 0 else 1
        
        pagination_meta = PaginationMeta(
            page=filters.page,
            page_size=filters.page_size,
            total_records=total_records,
            total_pages=total_pages
        )
        
        items = [OrderResponse.model_validate(order) for order in orders]
        logger.info(f"Retrieved page {filters.page} containing {len(items)} orders (Total: {total_records}).")
        
        return PaginatedResponse(items=items, pagination=pagination_meta)

    async def update_order_status(self, order_id: uuid.UUID, update_data: OrderUpdateStatus) -> OrderResponse:
        """Updates the status of an existing order."""
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            logger.warning(f"Failed to update status: Order {order_id} not found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found."
            )
        
        updated_order = await self.order_repo.update_status(order, update_data.status)
        await self.session.commit()
        logger.info(f"Order {order_id} status updated to {update_data.status.value}.")
        
        # Create response model for REST and WebSocket broadcast
        response_model = OrderResponse.model_validate(updated_order)
        
        # Broadcast the change to all connected WebSocket clients
        payload = {
            "event": ORDER_STATUS_UPDATED,
            "order": response_model.model_dump(mode="json")
        }
        await manager.broadcast_json(payload)
        
        return response_model
