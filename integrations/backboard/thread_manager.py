"""
Thread manager for Backboard.io
Manages model transitions and context preservation
"""
from integrations.backboard.client import backboard_client


class ThreadManager:
    """
    Manages stateful threads for seamless model transitions.
    Allows switching between coding models (Gemini Pro) and inference models (GPT-4o).
    """
    
    def __init__(self):
        self.client = backboard_client
        self.session_threads: dict[str, str] = {}  # session_id -> thread_id
    
    async def get_or_create_thread(self, session_id: str) -> str:
        """Get existing thread or create new one for session"""
        if session_id in self.session_threads:
            return self.session_threads[session_id]
        
        thread = await self.client.create_thread(
            metadata={"session_id": session_id}
        )
        thread_id = thread["id"]
        self.session_threads[session_id] = thread_id
        return thread_id
    
    async def add_preference_context(
        self,
        session_id: str,
        preferences: dict,
    ):
        """Add user preferences as context early in thread"""
        thread_id = await self.get_or_create_thread(session_id)
        await self.client.add_message(
            thread_id=thread_id,
            role="system",
            content=f"User preferences: {preferences}",
            metadata={"type": "preference_context"},
        )
    
    async def run_with_model(
        self,
        session_id: str,
        model: str,
        prompt: str,
    ) -> str:
        """Run inference with specified model"""
        thread_id = await self.get_or_create_thread(session_id)
        
        # Add user message
        await self.client.add_message(
            thread_id=thread_id,
            role="user",
            content=prompt,
        )
        
        # Run inference
        result = await self.client.run_inference(
            thread_id=thread_id,
            model=model,
        )
        
        return result.get("content", "")


thread_manager = ThreadManager()
