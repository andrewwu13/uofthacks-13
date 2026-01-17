"""
Stability Agent - Conservative layout generation
Generates safe, validated layouts for user retention
Uses Backboard.io for stateful thread management
"""
from integrations.backboard.thread_manager import thread_manager
from agents.config import agent_config
import json
import os


class StabilityAgent:
    """
    Conservative anchor of the user experience.
    Generates layouts optimized for retention with 70% confidence threshold.
    Only serves modules the user has implicitly validated.
    Uses Backboard.io for stateful context preservation.
    """
    
    def __init__(self):
        self._system_prompt = None
        self.confidence_threshold = agent_config.stability_confidence_threshold
    
    @property
    def system_prompt(self) -> str:
        """Lazy load system prompt"""
        if self._system_prompt is None:
            self._system_prompt = self._load_prompt()
        return self._system_prompt
    
    def _load_prompt(self) -> str:
        """Load system prompt from file"""
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "stability_agent.txt")
        try:
            with open(prompt_path) as f:
                return f.read()
        except FileNotFoundError:
            return """You are a stability agent focused on user retention.
Generate safe, validated layouts based on confirmed user preferences.
Only recommend modules with high confidence scores."""
    
    async def generate(
        self,
        session_id: str,
        preferences: dict,
        available_modules: list[dict],
        page_type: str,
    ) -> dict:
        """
        Generate a conservative layout proposal.
        
        Args:
            session_id: User session identifier for thread management
            preferences: Aggregated user preferences
            available_modules: List of available UI modules
            page_type: Type of page (home, product, etc.)
            
        Returns:
            Layout proposal with module selections
        """
        # Inject user preferences early in thread for in-context learning
        await thread_manager.add_preference_context(session_id, preferences)
        
        # Filter modules by confidence threshold
        confident_modules = [
            m for m in available_modules
            if preferences.get("genre_weights", {}).get(m.get("genre"), 0) >= self.confidence_threshold
        ]
        
        input_data = {
            "preferences": preferences,
            "modules": confident_modules or available_modules[:10],  # Fallback to base
            "page_type": page_type,
            "threshold": self.confidence_threshold,
        }
        
        prompt = f"{self.system_prompt}\n\nGenerate a layout for:\n{json.dumps(input_data)}"
        
        response = await thread_manager.run_with_model(
            session_id=session_id,
            model=agent_config.stability_agent_model,
            prompt=prompt,
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"sections": [], "raw_response": response}


stability_agent = StabilityAgent()
