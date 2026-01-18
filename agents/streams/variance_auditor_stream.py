"""
Stream 3: Variance Auditor - analyzes "loud" module responses for A/B testing
Runs on 5-second batch interval, only active when loud modules are in viewport
Uses Backboard.io for stateful thread management
"""
from integrations.backboard.thread_manager import thread_manager
from agents.config import agent_config
import json
import os


class VarianceAuditorStream:
    """
    Focuses on "loud" modules injected for hypothesis testing.
    Validates prediction model by analyzing engagement delta.
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
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "variance_auditor.txt")
        try:
            with open(prompt_path) as f:
                return f.read()
        except FileNotFoundError:
            return "You are a variance auditor. Analyze A/B test results from loud modules."
    
    async def process(
        self,
        session_id: str,
        loud_module_events: list[dict],
        baseline_engagement: dict,
    ) -> dict:
        """
        Audit loud module engagement.
        
        Args:
            session_id: User session identifier for thread management
            loud_module_events: Interactions with loud modules
            baseline_engagement: Baseline engagement metrics
            
        Returns:
            Reward signals and variance analysis
        """
        if not loud_module_events:
            return {"active": False, "signals": []}
        
        input_data = {
            "loud_events": loud_module_events,
            "baseline": baseline_engagement,
        }
        
        prompt = f"{self.system_prompt}\n\nAnalyze the following data:\n{json.dumps(input_data)}"
        
        response = await thread_manager.run_with_model(
            session_id=session_id,
            model=agent_config.variance_auditor_model,
            prompt=prompt,
        )
        
        try:
            result = json.loads(response)
            # Add reward signals based on engagement
            for event in loud_module_events:
                if event.get("dwell_time_ms", 0) > 2000:
                    result.setdefault("signals", []).append({
                        "module_id": event["module_id"],
                        "genre": event.get("genre"),
                        "reward": 1.0,  # Positive signal
                    })
                elif event.get("scroll_velocity", 0) > 500:
                    result.setdefault("signals", []).append({
                        "module_id": event["module_id"],
                        "genre": event.get("genre"),
                        "reward": -1.0,  # Negative signal (scrolled past quickly)
                    })
            return result
        except json.JSONDecodeError:
            return {"active": True, "signals": [], "analysis": response}


variance_auditor_stream = VarianceAuditorStream()
