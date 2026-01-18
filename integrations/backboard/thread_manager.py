"""
Thread manager for Backboard.io
Manages model transitions and context preservation
"""
from integrations.backboard.client import backboard_client


# Model mapping: our config names -> Backboard provider/model pairs
MODEL_MAPPING = {
    # Ultra-low cost models
    "12thD/ko-Llama-3-8B-sft-v0.3": ("12thD", "12thD/ko-Llama-3-8B-sft-v0.3"),
    "12thD/I-SOLAR-10.7B-dpo-sft-v0.2": ("12thD", "12thD/I-SOLAR-10.7B-dpo-sft-v0.2"), 
}

FALLBACK_MODEL = "12thD/I-SOLAR-10.7B-dpo-sft-v0.2"


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
        """Add user preferences as context early in thread (memory disabled to save costs)"""
        thread_id = await self.get_or_create_thread(session_id)
        
        # Add preferences as a message with memory DISABLED
        await self.client.add_message(
            thread_id=thread_id,
            content=f"User preferences context: {preferences}",
            memory="off", # FORCE OFF to prevent expensive reads
            stream=False,
        )
    
    async def run_with_model(
        self,
        session_id: str,
        model: str,
        prompt: str,
        memory_mode: str = "off",  # Argument preserved for API compatibility but ignored
    ) -> str:
        """Run inference with specified model (Memory enforced OFF) with fallback"""
        thread_id = await self.get_or_create_thread(session_id)
        
        # 1. Attempt with primary model
        try:
            return await self._execute_inference(thread_id, model, prompt)
        except Exception as e:
            print(f"[ThreadManager] Primary model '{model}' failed: {e}")
            
            # 2. Attempt fallback if different
            if model != FALLBACK_MODEL:
                print(f"[ThreadManager] Retrying with fallback model '{FALLBACK_MODEL}'...")
                try:
                    return await self._execute_inference(thread_id, FALLBACK_MODEL, prompt)
                except Exception as fallback_error:
                    print(f"[ThreadManager] Fallback model failed: {fallback_error}")
            
            # Re-raise if all attempts fail
            raise e

    async def _execute_inference(self, thread_id: str, model: str, prompt: str) -> str:
        """Execute single inference request"""
        # Map our model name to Backboard provider/model
        # Default to using the model name as the provider if unknown, often works for generic APIs
        if model in MODEL_MAPPING:
            llm_provider, model_name = MODEL_MAPPING[model]
        else:
            # Fallback: assume provider is "12thD" for unknown models to avoid accidental high costs
            llm_provider = "12thD" 
            model_name = model

        return await self.client.run_inference(
            thread_id=thread_id,
            prompt=prompt,
            llm_provider=llm_provider,
            model_name=model_name,
            memory="off", # FORCE OFF to prevent expensive reads
        )


thread_manager = ThreadManager()
