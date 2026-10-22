"""Main FastAPI Application Entrypoint for Carrier-Grade Telecom RCA & SLA Subsystem."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.api.routes_rca import router as rca_router
from backend.app.api.routes_hitl import router as hitl_router
from backend.app.api.routes_dashboard import router as dashboard_router, ensure_fixtures_loaded
from backend.app.api.websocket import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure fixtures are loaded in memory
    logger.info(f"Starting {settings.PROJECT_NAME} in [{settings.ENVIRONMENT}] mode.")
    logger.info(f"Use Fixtures Mode: {settings.USE_FIXTURES}, Mock Bedrock: {settings.MOCK_BEDROCK}")
    ensure_fixtures_loaded()
    yield
    # Shutdown
    logger.info("Shutting down Telecom RCA service.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0",
    description="Person C Subsystem: Governed Agentic AI, SLA Liability (LASM), and Carrier NOC Dashboard.",
    lifespan=lifespan,
)

# CORS Middleware for frontend dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API Routers
app.include_router(rca_router)
app.include_router(hitl_router)
app.include_router(dashboard_router)


@app.get("/healthz", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "person_c_rca_subsystem",
        "version": "2.0.0",
        "bedrock_mode": "mock" if settings.MOCK_BEDROCK else "live",
        "fixtures_mode": settings.USE_FIXTURES,
    }


@app.websocket("/ws/incidents")
async def websocket_incident_feed(websocket: WebSocket):
    """WebSocket feed for real-time dashboard events and probe feedback."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection open; receive client pings/messages if any
            data = await websocket.receive_text()
    except Exception:
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
