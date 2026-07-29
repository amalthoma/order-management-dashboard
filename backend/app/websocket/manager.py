import logging
import asyncio
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Singleton Connection Manager for WebSockets."""
    
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection and store it."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connected clients: {self.connection_count()}")

    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected WebSocket."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total connected clients: {self.connection_count()}")

    async def send_json(self, message: dict, websocket: WebSocket):
        """Send a JSON message to a single WebSocket."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Failed to send message to client. Removing connection. Error: {e}")
            self.disconnect(websocket)

    async def broadcast_json(self, message: dict):
        """Broadcast a JSON message to all connected WebSockets concurrently."""
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
        """Return the number of active connections."""
        return len(self.active_connections)

# Singleton instance
manager = ConnectionManager()
