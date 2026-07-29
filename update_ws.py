import os

base_dir = r"C:\Users\Amal Thomas\.gemini\antigravity\scratch\order_management"

files = {
    "backend/app/websocket/__init__.py": '"""WebSocket module for real-time notifications."""\n',
    "backend/app/websocket/events.py": """\"\"\"Constants for WebSocket events.\"\"\"

ORDER_STATUS_UPDATED = "ORDER_STATUS_UPDATED"
PING = "ping"
PONG = "pong"
""",
    "backend/app/websocket/manager.py": """import logging
import asyncio
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    \"\"\"Singleton Connection Manager for WebSockets.\"\"\"
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        \"\"\"Accept a new WebSocket connection and store it.\"\"\"
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connected clients: {self.connection_count()}")

    def disconnect(self, websocket: WebSocket):
        \"\"\"Remove a disconnected WebSocket.\"\"\"
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total connected clients: {self.connection_count()}")

    async def send_json(self, message: dict, websocket: WebSocket):
        \"\"\"Send a JSON message to a single WebSocket.\"\"\"
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send message to client. Removing connection. Error: {e}")
            self.disconnect(websocket)

    async def broadcast_json(self, message: dict):
        \"\"\"Broadcast a JSON message to all connected WebSockets concurrently.\"\"\"
        count = self.connection_count()
        if count == 0:
            return
            
        logger.info(f"Broadcast started for {count} clients.")
        
        # Use asyncio.gather to broadcast concurrently and prevent one slow client from blocking others
        tasks = []
        for connection in list(self.active_connections):
            tasks.append(self.send_json(message, connection))
            
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
        logger.info("Broadcast completed.")

    def connection_count(self) -> int:
        \"\"\"Return the number of active connections.\"\"\"
        return len(self.active_connections)

# Singleton instance
manager = ConnectionManager()
""",
    "backend/app/api/v1/endpoints/ws.py": """import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager
from app.websocket.events import PING, PONG

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/orders")
async def websocket_orders(websocket: WebSocket):
    \"\"\"
    WebSocket endpoint for real-time order updates.
    Clients will receive updates when an order status changes.
    \"\"\"
    await manager.connect(websocket)
    try:
        while True:
            # Receive text data
            data = await websocket.receive_text()
            
            # Simple ping/pong for keep-alive
            if data.lower() == PING:
                await manager.send_json({"type": PONG}, websocket)
            else:
                # Ignore unknown messages
                logger.debug(f"Received unknown message: {data}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
""",
    "backend/app/api/v1/router.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.api.dependencies import get_db
from app.database.session import check_database_health
from app.core.settings import settings
from app.api.v1.endpoints import auth, orders, dashboard, ws

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)
api_router.include_router(
    ws.router,
    prefix="/ws",
    tags=["Realtime"]
)

@api_router.get("/health", response_model=dict, tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    \"\"\"Health check endpoint.\"\"\"
    is_db_healthy = await check_database_health()
    return {
        "status": "healthy" if is_db_healthy else "degraded",
        "version": settings.VERSION,
        "database": "connected" if is_db_healthy else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
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
from app.websocket.manager import manager
from app.websocket.events import ORDER_STATUS_UPDATED

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
        
        # Create response model for REST and WebSocket broadcast
        response_model = OrderResponse.model_validate(updated_order)
        
        # Broadcast the change to all connected WebSocket clients
        payload = {
            "event": ORDER_STATUS_UPDATED,
            "order": response_model.model_dump(mode="json")
        }
        await manager.broadcast_json(payload)
        
        return response_model
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path.replace('/', os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("WebSocket files successfully generated.")
