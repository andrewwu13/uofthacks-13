"""
WebSocket message handlers
"""
from fastapi import WebSocket
from app.websocket.manager import WebSocketManager


async def handle_websocket_connection(
    websocket: WebSocket,
    session_id: str,
    manager: WebSocketManager
):
    """Handle a WebSocket connection lifecycle"""
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "ping":
                await websocket.send_json({"type": "pong"})
            elif message_type == "request_layout":
                # TODO: Fetch and send current layout
                pass
    except Exception:
        pass
    finally:
        manager.disconnect(websocket, session_id)
