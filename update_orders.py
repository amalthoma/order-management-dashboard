import os

base_dir = r"C:\Users\Amal Thomas\.gemini\antigravity\scratch\order_management"

files = {
    "backend/app/schemas/pagination.py": """from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class PaginationMeta(BaseModel):
    \"\"\"Metadata for paginated responses.\"\"\"
    page: int
    page_size: int
    total_records: int
    total_pages: int

class PaginatedResponse(BaseModel, Generic[T]):
    \"\"\"Generic wrapper for paginated lists of items.\"\"\"
    items: list[T]
    pagination: PaginationMeta
""",
    "backend/app/schemas/order_filter.py": """from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, Field
from app.core.enums import OrderStatus

class OrderFilter(BaseModel):
    \"\"\"Schema for filtering, sorting, and paginating orders.\"\"\"
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
""",
    "backend/app/repositories/order_repository.py": """import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order
from app.schemas.order import OrderCreate
from app.core.enums import OrderStatus
from app.schemas.order_filter import OrderFilter
from datetime import datetime, time

class OrderRepository:
    \"\"\"Repository for managing Order database operations.\"\"\"

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(self, order_in: OrderCreate, user_id: uuid.UUID) -> Order:
        \"\"\"Create a new order.\"\"\"
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
        \"\"\"Retrieve an order by its UUID.\"\"\"
        result = await self.session.execute(select(Order).where(Order.id == order_id))
        return result.scalars().first()

    async def list_orders(self) -> list[Order]:
        \"\"\"List all orders.\"\"\"
        result = await self.session.execute(select(Order).order_by(Order.created_at.desc(), Order.id.desc()))
        return list(result.scalars().all())

    async def update_status(self, db_order: Order, new_status: OrderStatus) -> Order:
        \"\"\"Update the status of an existing order.\"\"\"
        db_order.status = new_status
        await self.session.flush()
        await self.session.refresh(db_order)
        return db_order

    async def list_orders_filtered(self, filters: OrderFilter) -> tuple[list[Order], int]:
        \"\"\"List orders with filtering, sorting, and pagination.\"\"\"
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
""",
    "backend/app/services/order_service.py": """import uuid
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

logger = logging.getLogger(__name__)

class OrderService:
    \"\"\"Service layer for order management.\"\"\"

    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_repo = OrderRepository(session)

    async def create_order(self, order_in: OrderCreate, user_id: uuid.UUID) -> OrderResponse:
        \"\"\"Creates a new order.\"\"\"
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
        \"\"\"Retrieves an order by its ID.\"\"\"
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
        \"\"\"Lists all orders.\"\"\"
        orders = await self.order_repo.list_orders()
        logger.info(f"Retrieved {len(orders)} orders.")
        return [OrderResponse.model_validate(order) for order in orders]

    async def list_orders_filtered(self, filters: OrderFilter) -> PaginatedResponse[OrderResponse]:
        \"\"\"Lists orders with filtering, sorting, and pagination.\"\"\"
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
        \"\"\"Updates the status of an existing order.\"\"\"
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
""",
    "backend/app/api/v1/endpoints/orders.py": """import uuid
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
    \"\"\"Create a new order.\"\"\"
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
    \"\"\"List orders with filtering, sorting, and pagination.\"\"\"
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
    \"\"\"Retrieve details of a specific order.\"\"\"
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
    \"\"\"Update the status of an order.\"\"\"
    order_service = OrderService(db)
    order = await order_service.update_order_status(order_id, update_data)
    return StandardResponse(
        data=order,
        message="Order status updated successfully"
    )
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path.replace('/', os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Files successfully generated.")
