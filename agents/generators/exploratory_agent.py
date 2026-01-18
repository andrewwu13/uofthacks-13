"""
Exploratory Agent - Novel layout generation
Drives UI evolution by testing untested aesthetic territories
Uses Backboard.io for stateful thread management
"""
from integrations.backboard.thread_manager import thread_manager
from agents.config import agent_config
import json
import os


class ExploratoryAgent:
    """
    High-temperature agent for novelty and evolution.
    Probes untested aesthetic territories with "loud" modules.
    Can mutate atomic design tokens (font weight, colors, radii).
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
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "exploratory_agent.txt")
        try:
            with open(prompt_path) as f:
                return f.read()
        except FileNotFoundError:
            return """You are an exploratory agent focused on UI evolution.
Your goal is to probe untested aesthetic territories and find new preferences.
You can mutate design tokens and inject loud modules for A/B testing.
Be creative but don't make the experience unusable."""
    
    async def generate(
        self,
        session_id: str,
        preferences: dict,
        available_modules: list[dict],
        preference_voids: list[str],
        page_type: str,
    ) -> dict:
        """
        Generate an exploratory layout proposal.
        
        Args:
            session_id: User session identifier for thread management
            preferences: Current user preferences
            available_modules: List of available UI modules
            preference_voids: Genres/styles not yet tested
            page_type: Type of page
            
        Returns:
            Exploratory layout with loud modules and token mutations
        """
        # Inject user preferences early in thread for in-context learning
        await thread_manager.add_preference_context(session_id, preferences)
        
        input_data = {
            "preferences": preferences,
            "modules": available_modules,
            "voids": preference_voids,
            "page_type": page_type,
        }
        
        prompt = f"{self.system_prompt}\n\nGenerate an exploratory layout for:\n{json.dumps(input_data)}"
        
        response = await thread_manager.run_with_model(
            session_id=session_id,
            model=agent_config.exploratory_agent_model,
            prompt=prompt,
        )
        
        try:
            result = json.loads(response)
            # Mark exploratory modules as "loud"
            for section in result.get("sections", []):
                for module in section.get("modules", []):
                    if module.get("genre") in preference_voids:
                        module["is_loud"] = True
            return result
        except json.JSONDecodeError:
            return {"sections": [], "token_mutations": {}, "raw_response": response}
    
    def suggest_token_mutations(self, preferences: dict) -> dict:
        """
        Suggest atomic design token mutations for micro-testing.
        
        Returns:
            Suggested mutations for font weight, colors, radii, etc.
        """
        mutations = {}
        
        # If font weight not yet established, try variations
        if not preferences.get("preferred_font_weight"):
            mutations["font_weight"] = [400, 500, 600, 700]
        
        # If border radius not established, try variations
        if not preferences.get("preferred_border_radius"):
            mutations["border_radius"] = [0, 4, 8, 16]
        
        return mutations


exploratory_agent = ExploratoryAgent()
