"""WebSocket connection manager for real-time carrier NOC dashboard feeds."""

import json
from typing import List
from fastapi import WebSocket, WebSocketDisconnect
from backend.app.core.logging import logger


class ConnectionManager:
    """Manages active WebSocket connections to broadcast incident updates."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcasts a JSON message to all connected dashboards."""
        data = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(data)
            except Exception as e:
                logger.warning(f"Error sending message to WebSocket client: {e}")
                self.disconnect(connection)


ws_manager = ConnectionManager()
