import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order
from app.schemas.order import OrderCreate
from app.core.enums import OrderStatus
from app.schemas.order_filter import OrderFilter
from datetime import datetime, time

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

    async def list_orders_filtered(self, filters: OrderFilter) -> tuple[list[Order], int]:
        """List orders with filtering, sorting, and pagination."""
        stmt = select(Order)
        count_stmt = select(func.count(Order.id))
        
        # Search by customer_name
        if filters.search:
            search_filter = Order.customer_name.ilike(f"%{filters.search}%")
            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)
            
        # Filter by status
        if filters.status:
            stmt = stmt.where(Order.status == filters.status)
            count_stmt = count_stmt.where(Order.status == filters.status)
            
        # Filter by date range
        if filters.start_date:
            start_dt = datetime.combine(filters.start_date, time.min)
            stmt = stmt.where(Order.created_at >= start_dt)
            count_stmt = count_stmt.where(Order.created_at >= start_dt)
            
        if filters.end_date:
            end_dt = datetime.combine(filters.end_date, time.max)
            stmt = stmt.where(Order.created_at <= end_dt)
            count_stmt = count_stmt.where(Order.created_at <= end_dt)
            
        # Sorting
        sort_column = getattr(Order, filters.sort_by)
        if filters.sort_order == "desc":
            stmt = stmt.order_by(sort_column.desc(), Order.id.desc())
        else:
            stmt = stmt.order_by(sort_column.asc(), Order.id.asc())
            
        # Pagination
        offset = (filters.page - 1) * filters.page_size
        stmt = stmt.offset(offset).limit(filters.page_size)
        
        # Execute queries
        total_records_result = await self.session.execute(count_stmt)
        total_records = total_records_result.scalar() or 0
        
        records_result = await self.session.execute(stmt)
        orders = list(records_result.scalars().all())
        
        return orders, total_records
