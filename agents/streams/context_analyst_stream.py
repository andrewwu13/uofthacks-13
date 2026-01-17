"""
Stream 2: Context Analyst - correlates motor state with UI interactions
Runs on 5-second batch interval to reduce API costs
Uses Backboard.io for stateful thread management
"""
from integrations.backboard.thread_manager import thread_manager
from agents.config import agent_config
import json
import os


class ContextAnalystStream:
    """
    Synthesizes motor state data with semantic page interactions.
    Identifies correlations between user's physical state and UI engagement.
    Uses Backboard.io for stateful context preservation.
    """
    
    def __init__(self):
        self._system_prompt = None
    
    @property
    def system_prompt(self) -> str:
        """Lazy load system prompt"""
        if self._system_prompt is None:
            self._system_prompt = self._load_prompt()
        return self._system_prompt
    
    def _load_prompt(self) -> str:
        """Load system prompt from file"""
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "context_analyst.txt")
        try:
            with open(prompt_path) as f:
                return f.read()
        except FileNotFoundError:
            return "You are a context analyst. Analyze user behavior and preferences."
    
    async def process(
        self,
        session_id: str,
        motor_state: dict,
        interactions: list[dict],
        current_preferences: dict,
    ) -> dict:
        """
        Analyze context from motor state and interactions.
        
        Args:
            session_id: User session identifier for thread management
            motor_state: Current motor state from stream 1
            interactions: Recent UI interactions (hovers, clicks, etc.)
            current_preferences: Current preference weights
            
        Returns:
            Updated preference weights and analysis
        """
        # Inject user preferences early in thread for in-context learning
        await thread_manager.add_preference_context(session_id, current_preferences)
        
        input_data = {
            "motor_state": motor_state,
            "interactions": interactions,
            "current_preferences": current_preferences,
        }
        
        prompt = f"{self.system_prompt}\n\nAnalyze the following data:\n{json.dumps(input_data)}"
        
        response = await thread_manager.run_with_model(
            session_id=session_id,
            model=agent_config.context_analyst_model,
            prompt=prompt,
        )
        
        # Parse response and extract preference updates
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"preference_updates": {}, "insights": response}


context_analyst_stream = ContextAnalystStream()