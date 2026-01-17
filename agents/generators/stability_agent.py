"""
Stability Agent - Conservative layout generation
Generates safe, validated layouts for user retention
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from agents.config import agent_config
import json


class StabilityAgent:
    """
    Conservative anchor of the user experience.
    Generates layouts optimized for retention with 70% confidence threshold.
    Only serves modules the user has implicitly validated.
    """
    
    def __init__(self):
        self.model = ChatOpenAI(
            model=agent_config.stability_agent_model,
            temperature=0.3,  # Low temperature for consistency
        )
        self.confidence_threshold = agent_config.stability_confidence_threshold
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._load_prompt()),
            ("user", "{input}"),
        ])
    
    def _load_prompt(self) -> str:
        """Load system prompt from file"""
        try:
            with open("agents/prompts/stability_agent.txt") as f:
                return f.read()
        except FileNotFoundError:
            return """You are a stability agent focused on user retention.
Generate safe, validated layouts based on confirmed user preferences.
Only recommend modules with high confidence scores."""
    
    async def generate(
        self,
        preferences: dict,
        available_modules: list[dict],
        page_type: str,
    ) -> dict:
        """
        Generate a conservative layout proposal.
        
        Args:
            preferences: Aggregated user preferences
            available_modules: List of available UI modules
            page_type: Type of page (home, product, etc.)
            
        Returns:
            Layout proposal with module selections
        """
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
        
        chain = self.prompt | self.model
        response = await chain.ainvoke({"input": json.dumps(input_data)})
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"sections": [], "raw_response": response.content}


stability_agent = StabilityAgent()
