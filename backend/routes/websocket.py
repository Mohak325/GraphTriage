"""WebSocket endpoint for live streaming of RCA execution steps and real-time graph updates."""

import json
import logging
from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSocket Realtime"])


class ConnectionManager:
    """Manages active WebSocket client connections subscribed to RCA execution events."""

    def __init__(self):
        # Maps rca_id -> list of active WebSocket connections
        self.active_subscriptions: Dict[str, List[WebSocket]] = {}
        # Global broadcast listeners
        self.global_listeners: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, rca_id: str):
        await websocket.accept()
        if rca_id not in self.active_subscriptions:
            self.active_subscriptions[rca_id] = []
        self.active_subscriptions[rca_id].append(websocket)
        logger.info(f"WebSocket client connected to RCA channel '{rca_id}'. Total subscribers: {len(self.active_subscriptions[rca_id])}")

    def disconnect(self, websocket: WebSocket, rca_id: str):
        if rca_id in self.active_subscriptions:
            if websocket in self.active_subscriptions[rca_id]:
                self.active_subscriptions[rca_id].remove(websocket)
            if not self.active_subscriptions[rca_id]:
                del self.active_subscriptions[rca_id]
        logger.info(f"WebSocket client disconnected from RCA channel '{rca_id}'.")

    async def send_to_channel(self, rca_id: str, message: dict):
        """Broadcast payload to all clients subscribed to a specific RCA ID."""
        if rca_id in self.active_subscriptions:
            payload_str = json.dumps(message)
            stale_connections = []
            for ws in self.active_subscriptions[rca_id]:
                try:
                    await ws.send_text(payload_str)
                except Exception:
                    stale_connections.append(ws)
            for ws in stale_connections:
                self.disconnect(ws, rca_id)

    async def broadcast_global(self, message: dict):
        """Broadcast event to all connected dashboard clients."""
        payload_str = json.dumps(message)
        stale = []
        for ws in self.global_listeners:
            try:
                await ws.send_text(payload_str)
            except Exception:
                stale.append(ws)
        for ws in stale:
            if ws in self.global_listeners:
                self.global_listeners.remove(ws)


manager = ConnectionManager()


@router.websocket("/ws/rca/{rca_id}")
async def websocket_rca_stream(websocket: WebSocket, rca_id: str):
    """Real-time bi-directional streaming endpoint for RCA workflow updates."""
    await manager.connect(websocket, rca_id)
    try:
        # Send initial confirmation handshake
        await websocket.send_text(json.dumps({
            "event": "connected",
            "rca_id": rca_id,
            "message": f"Successfully subscribed to real-time events for investigation '{rca_id}'"
        }))

        # Keep connection open and handle incoming client commands (e.g., ping or cancellation)
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("action") == "ping":
                    await websocket.send_text(json.dumps({"event": "pong", "rca_id": rca_id}))
            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket, rca_id)
    except Exception as exc:
        logger.error(f"WebSocket connection error on rca_id {rca_id}: {exc}")
        manager.disconnect(websocket, rca_id)
