"""
Stream 2: Context Analyst - correlates motor state with UI interactions
Runs on 5-second batch interval to reduce API costs
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from agents.config import agent_config
import json
import os


class ContextAnalystStream:
    """
    Synthesizes motor state data with semantic page interactions.
    Identifies correlations between user's physical state and UI engagement.
    """
    
    def __init__(self):
        self._model = None
        self._prompt = None
    
    @property
    def model(self):
        """Lazy initialization of LLM model"""
        if self._model is None:
            self._model = ChatOpenAI(
                model=agent_config.context_analyst_model,
                temperature=0.3,
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
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "context_analyst.txt")
        try:
            with open(prompt_path) as f:
                return f.read()
        except FileNotFoundError:
            return "You are a context analyst. Analyze user behavior and preferences."
    
    async def process(
        self,
        motor_state: dict,
        interactions: list[dict],
        current_preferences: dict,
    ) -> dict:
        """
        Analyze context from motor state and interactions.
        
        Args:
            motor_state: Current motor state from stream 1
            interactions: Recent UI interactions (hovers, clicks, etc.)
            current_preferences: Current preference weights
            
        Returns:
            Updated preference weights and analysis
        """
        input_data = {
            "motor_state": motor_state,
            "interactions": interactions,
            "current_preferences": current_preferences,
        }
        
        chain = self.prompt | self.model
        response = await chain.ainvoke({"input": json.dumps(input_data)})
        
        # Parse response and extract preference updates
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"preference_updates": {}, "insights": response.content}


context_analyst_stream = ContextAnalystStream()