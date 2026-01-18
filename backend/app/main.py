"""
Gen UI Backend - FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
import logging
import time

from app.config import settings
from app.db.mongo_client import mongo_client
from app.db.redis_client import redis_client
from app.api.endpoints import router as api_router
from app.api.events import router as events_router
from app.sse.publisher import sse_publisher
from app.websocket.manager import manager
from app.websocket.handlers import handle_websocket_connection

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events for database connections.
    """
    # =========================================
    # Startup
    # =========================================
    logger.info("Starting Gen UI Backend...")
    
    # Connect to MongoDB
    try:
        await mongo_client.connect()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        # Continue without MongoDB for graceful degradation
    
    # Connect to Redis
    try:
        await redis_client.connect()
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
    
    # Initialize vector store for module matching
    try:
        logger.info("Initializing vector store...")
        from app.vector import initialize_vector_store
        initialize_vector_store()
    except Exception as e:
        logger.warning(f"Failed to initialize vector store: {e}")
    
    logger.info("Gen UI Backend started successfully")
    
    yield  # Application runs here
    
    # =========================================
    # Shutdown
    # =========================================
    logger.info("Shutting down Gen UI Backend...")
    
    await mongo_client.disconnect()
    await redis_client.disconnect()
    
    logger.info("Gen UI Backend shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Gen UI Backend",
    description="AI-powered self-evolving storefront backend",
    version="1.0.0",
    lifespan=lifespan,
)

# =========================================
# Middleware
# =========================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses"""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# =========================================
# Include API Routes
# =========================================

app.include_router(api_router)
app.include_router(events_router, prefix="/telemetry", tags=["Telemetry"])


# =========================================
# Health Check Endpoints
# =========================================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for container orchestration.
    Returns status of all connected services.
    """
    mongo_health = await mongo_client.health_check()
    redis_health = await redis_client.health_check()
    
    all_healthy = (
        mongo_health.get("status") == "connected" and
        redis_health.get("status") == "connected"
    )
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": {
            "mongodb": mongo_health,
            "redis": redis_health,
        }
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "name": "Gen UI Backend",
        "version": "1.0.0",
        "docs": "/docs",
    }


# =========================================
# SSE and WebSocket Endpoints
# =========================================

@app.get("/stream/{session_id}")
async def stream(session_id: str):
    """SSE stream for layout updates"""
    return EventSourceResponse(sse_publisher.subscribe(session_id))


@app.post("/debug/publish_layout/{session_id}")
async def debug_publish_layout(session_id: str, request: Request):
    """Debug endpoint to trigger layout updates for testing SSE isolation."""
    payload = await request.json()
    await sse_publisher.publish_layout_update(session_id, payload)
    return {"status": "published", "session_id": session_id}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket, session_id: str):
    await handle_websocket_connection(websocket, session_id, manager)


# =========================================
# Exception Handlers
# =========================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# =========================================
# Run with: uvicorn app.main:app --reload
# =========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
