from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.api.events import router as events_router
from app.sse.publisher import sse_publisher
from app.websocket.manager import manager
from app.websocket.handlers import handle_websocket_connection
from sse_starlette.sse import EventSourceResponse

app = FastAPI(title="Self-Evolving AI Storefront")

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
