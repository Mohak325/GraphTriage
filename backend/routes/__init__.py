"""API route definitions for GraphTriage Backend."""

from backend.routes.rca import router as rca_router
from backend.routes.graph import router as graph_router
from backend.routes.ingestion import router as ingestion_router
from backend.routes.websocket import router as ws_router

__all__ = ["rca_router", "graph_router", "ingestion_router", "ws_router"]
