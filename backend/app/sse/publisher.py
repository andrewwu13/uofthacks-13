"""
Server-Sent Events publisher
"""
from sse_starlette.sse import EventSourceResponse
from typing import AsyncGenerator
import asyncio
import json


class SSEPublisher:
    """Manages SSE connections for layout updates"""
    
    def __init__(self):
        self.subscribers: dict = {}
    
    async def subscribe(self, session_id: str) -> AsyncGenerator:
        """Subscribe to layout updates for a session"""
        queue = asyncio.Queue()
        
        if session_id not in self.subscribers:
            self.subscribers[session_id] = []
        self.subscribers[session_id].append(queue)
        
        try:
            while True:
                data = await queue.get()
                yield {
                    "event": data["event"],
                    "data": json.dumps(data["payload"]),
                }
        finally:
            self.subscribers[session_id].remove(queue)
            if not self.subscribers[session_id]:
                del self.subscribers[session_id]
    
    async def publish_layout(self, session_id: str, layout: dict):
        """Publish layout update to all subscribers"""
        if session_id in self.subscribers:
            for queue in self.subscribers[session_id]:
                await queue.put({
                    "event": "layout_update",
                    "payload": layout,
                })


# Global SSE publisher instance
sse_publisher = SSEPublisher()
