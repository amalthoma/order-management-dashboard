import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager
from app.websocket.events import PING, PONG

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/orders")
async def websocket_orders(websocket: WebSocket):
    """
    WebSocket endpoint for real-time order updates.
    Clients will receive updates when an order status changes.
    """
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
