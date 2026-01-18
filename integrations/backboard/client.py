"""
Backboard.io API client
For stateful thread management and agentic memory
Based on official Backboard API docs: https://app.backboard.io/api
"""
import httpx
import os
from typing import Optional, Dict, Any, List
from pathlib import Path

# Load .env from project root (3 levels up: client.py -> backboard -> integrations -> root)
from dotenv import load_dotenv
project_root = Path(__file__).resolve().parents[2]
env_path = project_root / ".env"
if not env_path.exists():
    # Try one level up if running from backend
    env_path = project_root.parent / ".env"
load_dotenv(env_path)


class BackboardClient:
    """
    Client for Backboard.io Stateful Thread Management.
    Preserves conversation state server-side for seamless model transitions.
    """
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.environ.get("BACKBOARD_API_KEY", "")
        self.base_url = "https://app.backboard.io/api"
        self.client = httpx.AsyncClient(timeout=60.0)
        self._assistant_id: Optional[str] = None
        
        # Debug: Print API key info on initialization
        if self.api_key:
            masked_key = self.api_key[:8] + "..." + self.api_key[-4:] if len(self.api_key) > 12 else "***"
            print(f"[Backboard] Initialized with API key: {masked_key}")
            print(f"[Backboard] Base URL: {self.base_url}")
        else:
            print("[Backboard] WARNING: No API key found! Set BACKBOARD_API_KEY env var.")
    
    @property
    def headers(self) -> dict:
        return {
            "X-API-Key": self.api_key,
        }
    
    async def create_assistant(
        self,
        name: str = "UofTHacks Agent",
        system_prompt: str = "You are a helpful AI assistant.",
        tools: Optional[List[Dict]] = None,
    ) -> dict:
        """Create an assistant"""
        payload = {
            "name": name,
            "system_prompt": system_prompt,
        }
        if tools:
            payload["tools"] = tools
        
        response = await self.client.post(
            f"{self.base_url}/assistants",
            headers=self.headers,
            json=payload,
        )
        response.raise_for_status()
        result = response.json()
        self._assistant_id = result.get("assistant_id")
        return result
    
    async def get_or_create_assistant(self, name: str = "UofTHacks Agent") -> str:
        """Get existing assistant or create a new one"""
        if self._assistant_id:
            return self._assistant_id
        
        # Try to list existing assistants
        try:
            response = await self.client.get(
                f"{self.base_url}/assistants",
                headers=self.headers,
            )
            response.raise_for_status()
            assistants = response.json()
            
            # Find existing assistant by name
            for assistant in assistants:
                if assistant.get("name") == name:
                    self._assistant_id = assistant.get("assistant_id")
                    return self._assistant_id
        except Exception:
            pass
        
        # Create new assistant
        result = await self.create_assistant(name=name)
        return result.get("assistant_id")
    
    async def create_thread(self, assistant_id: Optional[str] = None) -> dict:
        """Create a new conversation thread under an assistant"""
        if not assistant_id:
            assistant_id = await self.get_or_create_assistant()
        
        response = await self.client.post(
            f"{self.base_url}/assistants/{assistant_id}/threads",
            headers=self.headers,
            json={},
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
        content: str,
        llm_provider: str = "openrouter",
        model_name: str = "deepseek/deepseek-v3.2",
        memory: str = "Auto",
        stream: bool = False,
    ) -> dict:
        """Add message to thread and get response"""
        # Use form data as per API docs
        data = {
            "content": content,
            "llm_provider": llm_provider,
            "model_name": model_name,
            "memory": memory,
            "stream": str(stream).lower(),
            "send_to_llm": "true",
        }
        
        # Debug: Print the LLM request details
        print(f"[Backboard] LLM Request: provider={llm_provider}, model={model_name}")
        
        response = await self.client.post(
            f"{self.base_url}/threads/{thread_id}/messages",
            headers=self.headers,
            data=data,
        )
        response.raise_for_status()
        return response.json()
    
    async def run_inference(
        self,
        thread_id: str,
        prompt: str,
        llm_provider: str = "openrouter",
        model_name: str = "deepseek/deepseek-v3.2",
        memory: str = "Auto",
    ) -> str:
        """Run inference on thread with specified model and return content"""
        result = await self.add_message(
            thread_id=thread_id,
            content=prompt,
            llm_provider=llm_provider,
            model_name=model_name,
            memory=memory,
            stream=False,
        )
        return result.get("content", "")
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Singleton instance
backboard_client = BackboardClient()
