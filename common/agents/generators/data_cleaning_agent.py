import os
from typing import Dict, Any, List
from integrations.backboard.thread_manager import thread_manager
from agents.config import agent_config
from agents.concurrency_manager import llm_concurrency_manager

class DataCleaningAgent:
    """
    Phase 1 Agent: Converts raw telemetry and events into an objective descriptive paragraph.
    Uses strict 1-agent concurrency.
    """
    def __init__(self):
        self.model = agent_config.context_analyst_model # Reusing config for now
        
        # Load prompt
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "data_cleaner.txt")
        with open(prompt_path, "r") as f:
            self.system_prompt = f.read()

    async def clean(
        self,
        session_id: str,
        motor_state: str,
        metrics: Dict[str, Any],
        interactions: List[Dict[str, Any]]
    ) -> str:
        """
        Run the cleaning LLM call.
        """
        prompt = self.system_prompt.format(
            motor_state=motor_state,
            metrics=metrics,
            interactions=interactions
        )

        async with llm_concurrency_manager:
            try:
                print(f"[DataCleaningAgent] Running cleaning for {session_id}...")
                response = await thread_manager.run_with_model(
                    session_id=session_id,
                    model=self.model,
                    prompt=prompt
                )
                print(f"[DataCleaningAgent] Response: {response[:100]}...")
                return response.strip()
            except Exception as e:
                print(f"[DataCleaningAgent] Error: {e}")
                return f"User exhibited {motor_state} behavior with {len(interactions)} recorded interactions."

data_cleaning_agent = DataCleaningAgent()
