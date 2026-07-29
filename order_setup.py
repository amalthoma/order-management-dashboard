import os

base_dir = r"C:\Users\Amal Thomas\.gemini\antigravity\scratch\order_management"

files_to_create = {
    "backend/app/core/enums.py": """from enum import Enum

class OrderStatus(str, Enum):
    \"\"\"Enumeration for order statuses.\"\"\"
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
""",
    "backend/app/models/order.py": """import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Numeric, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.core.enums import OrderStatus

class Order(Base):
    \"\"\"Database model for orders.\"\"\"
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus, name="orderstatus_enum"), default=OrderStatus.PENDING, nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    created_by_user = relationship("User", back_populates="orders")
""",
    "backend/app/schemas/order.py": """import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.core.enums import OrderStatus

class OrderBase(BaseModel):
    \"\"\"Base schema for order data.\"\"\"
    customer_name: str = Field(..., max_length=150)
    amount: float = Field(..., gt=0, description="Amount must be greater than zero.")

class OrderCreate(OrderBase):
    \"\"\"Schema for creating a new order.\"\"\"
    pass

class OrderUpdateStatus(BaseModel):
    \"\"\"Schema for updating order status.\"\"\"
    status: OrderStatus

class OrderResponse(OrderBase):
    \"\"\"Schema for returning order data.\"\"\"
    id: uuid.UUID
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID

    model_config = {"from_attributes": True}
""",
    "backend/app/repositories/order_repository.py": """import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order
from app.schemas.order import OrderCreate
from app.core.enums import OrderStatus

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

    async def list_orders(self) -> Sequence[Order]:
        \"\"\"List all orders.\"\"\"
        result = await self.session.execute(select(Order).order_by(Order.created_at.desc()))
        return result.scalars().all()

    async def update_status(self, db_order: Order, new_status: OrderStatus) -> Order:
        \"\"\"Update the status of an existing order.\"\"\"
        db_order.status = new_status
        await self.session.flush()
        await self.session.refresh(db_order)
        return db_order
""",
    "backend/app/services/order_service.py": """import uuid
import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.order_repository import OrderRepository
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdateStatus
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
    response_model=StandardResponse[List[OrderResponse]],
    status_code=status.HTTP_200_OK,
    summary="List Orders"
)
async def list_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    \"\"\"List all orders.\"\"\"
    order_service = OrderService(db)
    orders = await order_service.list_orders()
    return StandardResponse(
        data=orders,
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

for path, content in files_to_create.items():
    full_path = os.path.join(base_dir, path.replace('/', os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Files created successfully.")
