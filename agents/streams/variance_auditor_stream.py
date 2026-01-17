"""
Stream 3: Variance Auditor - analyzes "loud" module responses for A/B testing
Runs on 5-second batch interval, only active when loud modules are in viewport
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from agents.config import agent_config
import json
import os


class VarianceAuditorStream:
    """
    Focuses on "loud" modules injected for hypothesis testing.
    Validates prediction model by analyzing engagement delta.
    """
    
    def __init__(self):
        self._model = None
        self._prompt = None
    
    @property
    def model(self):
        """Lazy initialization of LLM model"""
        if self._model is None:
            self._model = ChatOpenAI(
                model=agent_config.variance_auditor_model,
                temperature=0.2,
            )
        return self._model
    
    @property
    def prompt(self):
        """Lazy initialization of prompt template"""
        if self._prompt is None:
            self._prompt = ChatPromptTemplate.from_messages([
                ("system", self._load_prompt()),
                ("user", "{input}"),
            ])
        return self._prompt
    
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
        loud_module_events: list[dict],
        baseline_engagement: dict,
    ) -> dict:
        """
        Audit loud module engagement.
        
        Args:
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
        
        chain = self.prompt | self.model
        response = await chain.ainvoke({"input": json.dumps(input_data)})
        
        try:
            result = json.loads(response.content)
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
            return {"active": True, "signals": [], "analysis": response.content}


variance_auditor_stream = VarianceAuditorStream()
