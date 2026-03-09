import os
from integrations.backboard.thread_manager import thread_manager
from agents.config import agent_config
from agents.concurrency_manager import llm_concurrency_manager

class ShortContextAgent:
    """
    Phase 2 Agent: Analyzes immediate behavioral intent.
    Uses Lock:2 concurrency (runs in parallel with LongContextAgent).
    """
    def __init__(self):
        self.model = agent_config.context_analyst_model
        
        # Load prompt
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "short_context.txt")
        with open(prompt_path, "r") as f:
            self.system_prompt = f.read()

    async def analyze(self, session_id: str, behavioral_description: str) -> str:
        prompt = self.system_prompt.format(behavioral_description=behavioral_description)

        async with llm_concurrency_manager:
            try:
                response = await thread_manager.run_with_model(
                    session_id=session_id,
                    model=self.model,
                    prompt=prompt
                )
                return response.strip()
            except Exception as e:
                print(f"[ShortContextAgent] Error: {e}")
                return "User is browsing normally."

short_context_agent = ShortContextAgent()
