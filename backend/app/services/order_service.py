import uuid
import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdateStatus
from app.models.order import Order
from app.core.enums import OrderStatus

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
        return OrderResponse.model_validate(updated_order)
