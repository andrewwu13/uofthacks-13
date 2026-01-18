from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.api.events import router as events_router
from app.sse.publisher import sse_publisher
from app.websocket.manager import manager
from app.websocket.handlers import handle_websocket_connection
from app.db.mongo_client import mongo_client
from app.db.redis_client import redis_client
from sse_starlette.sse import EventSourceResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup: Connect to databases
    print("[Startup] Connecting to MongoDB...")
    await mongo_client.connect()
    print("[Startup] MongoDB connected")
    
    print("[Startup] Connecting to Redis...")
    await redis_client.connect()
    print("[Startup] Redis connected")
    
    # Initialize vector store for module matching
    print("[Startup] Initializing vector store...")
    from app.vector import initialize_vector_store
    initialize_vector_store()
    
    yield
    
    # Shutdown: Disconnect from databases
    print("[Shutdown] Disconnecting from MongoDB...")
    await mongo_client.disconnect()
    print("[Shutdown] Disconnecting from Redis...")
    await redis_client.disconnect()


app = FastAPI(title="Self-Evolving AI Storefront", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)
app.include_router(events_router, prefix="/telemetry", tags=["Telemetry"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/stream/{session_id}")
async def stream(session_id: str):
    # TODO: Initialize or recover persistent session state from DB here
    return EventSourceResponse(sse_publisher.subscribe(session_id))

@app.post("/debug/publish_layout/{session_id}")
async def debug_publish_layout(session_id: str, request: Request):
    """Debug endpoint to trigger layout updates for testing SSE isolation."""
    payload = await request.json()
    await sse_publisher.publish_layout_update(session_id, payload)
    return {"status": "published", "session_id": session_id}

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: str, session_id: str):
    await handle_websocket_connection(websocket, session_id, manager)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

