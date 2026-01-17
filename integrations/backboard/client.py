"""
Backboard.io API client
For stateful thread management and agentic memory
"""
import httpx
from typing import Optional, Dict, Any


class BackboardClient:
    """
    Client for Backboard.io Stateful Thread Management.
    Preserves conversation state server-side for seamless model transitions.
    """
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.base_url = "https://api.backboard.io/v1"
        self.client = httpx.AsyncClient()
    
    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def create_thread(self, metadata: Optional[Dict[str, Any]] = None) -> dict:
        """Create a new conversation thread"""
        response = await self.client.post(
            f"{self.base_url}/threads",
            headers=self.headers,
            json={"metadata": metadata or {}},
        )
        response.raise_for_status()
        return response.json()
    
    async def get_thread(self, thread_id: str) -> dict:
        """Get thread state"""
        response = await self.client.get(
            f"{self.base_url}/threads/{thread_id}",
            headers=self.headers,
        )
        response.raise_for_status()
        return response.json()
    
    async def add_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """Add message to thread"""
        response = await self.client.post(
            f"{self.base_url}/threads/{thread_id}/messages",
            headers=self.headers,
            json={
                "role": role,
                "content": content,
                "metadata": metadata or {},
            },
        )
        response.raise_for_status()
        return response.json()
    
    async def run_inference(
        self,
        thread_id: str,
        model: str = "gpt-4o",
        system_prompt: Optional[str] = None,
    ) -> dict:
        """Run inference on thread with specified model"""
        payload = {"model": model}
        if system_prompt:
            payload["system"] = system_prompt
        
        response = await self.client.post(
            f"{self.base_url}/threads/{thread_id}/runs",
            headers=self.headers,
            json=payload,
        )
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


backboard_client = BackboardClient()
