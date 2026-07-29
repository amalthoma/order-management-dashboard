import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order
from app.schemas.order import OrderCreate
from app.core.enums import OrderStatus

class OrderRepository:
    """Repository for managing Order database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(self, order_in: OrderCreate, user_id: uuid.UUID) -> Order:
        """Create a new order."""
        db_order = Order(
            customer_name=order_in.customer_name,
            amount=order_in.amount,
            created_by=user_id,
            status=OrderStatus.PENDING
        )
        self.session.add(db_order)
        await self.session.flush()
        await self.session.refresh(db_order)
        return db_order

    async def get_by_id(self, order_id: uuid.UUID) -> Order | None:
        """Retrieve an order by its UUID."""
        result = await self.session.execute(select(Order).where(Order.id == order_id))
        return result.scalars().first()

    async def list_orders(self) -> list[Order]:
        """List all orders."""
        result = await self.session.execute(select(Order).order_by(Order.created_at.desc(), Order.id.desc()))
        return list(result.scalars().all())

    async def update_status(self, db_order: Order, new_status: OrderStatus) -> Order:
        """Update the status of an existing order."""
        db_order.status = new_status
        await self.session.flush()
        await self.session.refresh(db_order)
        return db_order
