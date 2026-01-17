"""
Thread manager for Backboard.io
Manages model transitions and context preservation
"""
from integrations.backboard.client import backboard_client


# Model mapping: our config names -> Backboard provider/model pairs
MODEL_MAPPING = {
    "gemini-2.5-flash": ("google", "gemini-2.5-flash"),
    "gemini-2.5-pro": ("google", "gemini-2.5-pro"),
    "gpt-4o": ("openai", "gpt-4o"),
    "gpt-4o-mini": ("openai", "gpt-4o-mini"),
}


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
        
        thread = await self.client.create_thread()
        thread_id = thread.get("thread_id")
        self.session_threads[session_id] = thread_id
        return thread_id
    
    async def add_preference_context(
        self,
        session_id: str,
        preferences: dict,
    ):
        """Add user preferences as context early in thread (uses memory)"""
        thread_id = await self.get_or_create_thread(session_id)
        
        # Add preferences as a message with memory enabled
        await self.client.add_message(
            thread_id=thread_id,
            content=f"User preferences context: {preferences}",
            memory="Auto",
            stream=False,
        )
    
    async def run_with_model(
        self,
        session_id: str,
        model: str,
        prompt: str,
        memory_mode: str = "off",  # Default to off to save costs on high-frequency calls
    ) -> str:
        """Run inference with specified model"""
        thread_id = await self.get_or_create_thread(session_id)
        
        # Map our model name to Backboard provider/model
        llm_provider, model_name = MODEL_MAPPING.get(model, ("google", "gemini-2.5-flash"))
        
        # Run inference and get response
        content = await self.client.run_inference(
            thread_id=thread_id,
            prompt=prompt,
            llm_provider=llm_provider,
            model_name=model_name,
            memory=memory_mode,
        )
        
        return content


thread_manager = ThreadManager()
