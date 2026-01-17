"""
Gen UI Backend - FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from app.config import settings
from app.db.mongo_client import mongo_client
from app.db.redis_client import redis_client

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
# API Routes (to be added)
# =========================================

# TODO: Import and include routers
# from app.api.layout import router as layout_router
# from app.api.events import router as events_router
# from app.api.session import router as session_router
# from app.api.products import router as products_router

# app.include_router(layout_router, prefix="/api/layout", tags=["Layout"])
# app.include_router(events_router, prefix="/api/events", tags=["Events"])
# app.include_router(session_router, prefix="/api/session", tags=["Session"])
# app.include_router(products_router, prefix="/api/products", tags=["Products"])


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
