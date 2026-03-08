import os
import logging
from typing import List, Dict, Any
from integrations.backboard.thread_manager import thread_manager
from agents.config import agent_config
from agents.concurrency_manager import llm_concurrency_manager

logger = logging.getLogger(__name__)

class LongContextAgent:
    """
    Phase 2 Agent: Analyzes long-term patterns and recommendation impact.
    Uses Lock:2 concurrency (runs in parallel with ShortContextAgent).
    """
    def __init__(self):
        self.model = agent_config.context_analyst_model
        
        # Load prompt
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "long_context.txt")
        with open(prompt_path, "r") as f:
            self.system_prompt = f.read()

    async def analyze(self, session_id: str, behavioral_description: str, history: List[Dict[str, Any]]) -> str:
        # Format history for prompt
        history_str = "No recent history."
        if history:
            history_entries = []
            for entry in history[-5:]: # Use last 5 snapshots
                timestamp = entry.get("timestamp", "unknown")
                rec = entry.get("constraints_summary", {}).get("hard", {}).get("genre_weights", "unknown")
                history_entries.append(f"[{timestamp}] Rec: {rec}")
            history_str = "\n".join(history_entries)

        prompt = self.system_prompt.format(
            behavioral_description=behavioral_description,
            history=history_str
        )

        async with llm_concurrency_manager:
            try:
                response = await thread_manager.run_with_model(
                    session_id=session_id,
                    model=self.model,
                    prompt=prompt
                )
                return response.strip()
            except Exception as e:
                print(f"[LongContextAgent] Error: {e}")
                return "User behavior is consistent with previous patterns."

long_context_agent = LongContextAgent()
