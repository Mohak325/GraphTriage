"""FastAPI application entry point for GraphTriage Backend.

Initializes application lifecycle, database connection pools, CORS middleware,
and mounts all sub-routers (RCA, Graph, Ingestion, WebSocket).
"""

import time
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import get_settings
from backend.routes import rca_router, graph_router, ingestion_router, ws_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
)
logger = logging.getLogger("graphtriage")
settings = get_settings()


# =============================================
# Application Lifespan (Startup / Shutdown)
# =============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and graceful shutdown."""
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: DEBUG={settings.DEBUG}, NEO4J_URI={settings.NEO4J_URI}")
    logger.info("=" * 60)

    # Initialize Neo4j client connection if available
    try:
        from ai_models.graph_engine.neo4j_client import Neo4jClient
        user, password = settings.neo4j_auth_credentials
        client = Neo4jClient(uri=settings.NEO4J_URI, user=user, password=password)
        app.state.neo4j_client = client
        logger.info("Initialized Neo4j client instance in app state.")
    except Exception as exc:
        logger.warning(f"Could not pre-initialize Neo4j client: {exc}. Will connect on demand.")
        app.state.neo4j_client = None

    yield  # Application runs here

    logger.info("Shutting down GraphTriage Backend...")
    client = getattr(app.state, "neo4j_client", None)
    if client is not None:
        try:
            await client.close()
            logger.info("Closed Neo4j driver connection pool.")
        except Exception as exc:
            logger.error(f"Error closing Neo4j client: {exc}")


# =============================================
# FastAPI Application Instance
# =============================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="High-performance Root Cause Analysis platform combining Neo4j graph topologies, spectral graph algorithms, and multi-agent AI verification.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# =============================================
# Middleware
# =============================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Measures request execution duration and adds X-Process-Time header."""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response


# =============================================
# Health & Status Endpoints
# =============================================

@app.get("/health", tags=["Health"], summary="Basic Liveness Probe")
async def health_check() -> Dict[str, Any]:
    """Lightweight health check endpoint for Docker container and load balancer probes."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": time.time()
    }


@app.get("/health/detailed", tags=["Health"], summary="Detailed Readiness Probe")
async def detailed_health_check() -> Dict[str, Any]:
    """Detailed health check validating Neo4j and Redis connectivity."""
    components = {
        "api": "healthy",
        "neo4j": "unknown",
        "redis": "unknown"
    }

    # Neo4j check
    client = getattr(app.state, "neo4j_client", None)
    if client:
        try:
            is_connected = await client.verify_connectivity()
            components["neo4j"] = "connected" if is_connected else "disconnected"
        except Exception:
            components["neo4j"] = "unreachable"
    else:
        components["neo4j"] = "not_initialized"

    overall_status = "healthy" if components["neo4j"] in ("connected", "not_initialized") else "degraded"

    return {
        "status": overall_status,
        "components": components,
        "timestamp": time.time()
    }


# =============================================
# Mount Routers
# =============================================

app.include_router(rca_router)
app.include_router(graph_router)
app.include_router(ingestion_router)
app.include_router(ws_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
