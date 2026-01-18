"""
Agent configuration
"""
from pydantic import BaseModel
from typing import Literal


class AgentConfig(BaseModel):
    """Configuration for agent behavior"""
    
    # Stream frequencies
    motor_state_interval_ms: int = 100  # Near-constant
    context_analyst_interval_ms: int = 5000  # 5 second batch
    variance_auditor_interval_ms: int = 5000  # 5 second batch
    
    # Model configuration
    context_analyst_model: str = "deepseek-v3.2"  # Fast, cheap
    variance_auditor_model: str = "deepseek-v3.2"
    stability_agent_model: str = "deepseek-v3.2"  # More capable
    exploratory_agent_model: str = "deepseek-v3.2"
    
    # Thresholds
    stability_confidence_threshold: float = 0.7
    exploratory_temperature: float = 0.9
    
    # Motor state thresholds
    jitter_threshold: float = 0.5
    anxiety_threshold: float = 0.3
    determined_velocity_threshold: float = 500.0


class StreamState(BaseModel):
    """Shared state between agent streams"""
    session_id: str
    motor_state: Literal["idle", "determined", "browsing", "anxious", "jittery"] = "idle"
    motor_confidence: float = 0.0
    genre_weights: dict = {}
    recent_interactions: list = []
    loud_module_responses: list = []


agent_config = AgentConfig()
