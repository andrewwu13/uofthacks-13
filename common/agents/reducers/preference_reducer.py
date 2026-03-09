"""
Preference Reducer - Synthesizes analysis into a final Vibe Summary
"""

import os
from integrations.backboard.thread_manager import thread_manager
from agents.config import agent_config
from agents.concurrency_manager import llm_concurrency_manager

class PreferenceReducer:
    """
    Final Phase Agent: Synthesizes Short and Long context analysis into a 20-30 word vibe summary.
    Uses Lock:1 concurrency.
    """
    def __init__(self):
        self.model = agent_config.context_analyst_model
        
        # Load prompt
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "preference_reducer.txt")
        with open(prompt_path, "r") as f:
            self.system_prompt = f.read()

    async def reduce(
        self,
        session_id: str,
        short_context: str,
        long_context: str
    ) -> str:
        """
        Synthesize the two analysis outputs into a final vectorizable vibe summary.
        """
        prompt = self.system_prompt.format(
            short_context=short_context,
            long_context=long_context
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
                print(f"[PreferenceReducer] Error: {e}")
                return "New user seeking a standard, clean experience with a subtle secondary interest in minimalist aesthetics."

preference_reducer = PreferenceReducer()
