"""
WebSocket connection manager
"""
from fastapi import WebSocket
from typing import Dict, List
import json


class WebSocketManager:
    """Manages WebSocket connections for real-time layout updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove a WebSocket connection"""
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
    
    async def send_layout_update(self, session_id: str, layout: dict):
        """Send layout update to all connections for a session"""
        if session_id in self.active_connections:
            message = json.dumps({"type": "layout_update", "payload": layout})
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(message)
                except Exception:
                    pass  # Connection may have closed
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connections"""
        text = json.dumps(message)
        for connections in self.active_connections.values():
            for connection in connections:
                try:
                    await connection.send_text(text)
                except Exception:
                    pass
