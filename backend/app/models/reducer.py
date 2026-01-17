"""
Reducer output models matching the canonical user preference JSON
"""
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class VisualTraits(BaseModel):
    """Visual preference traits from reducer"""
    color_scheme: Literal["dark", "light", "vibrant"] = "light"
    corner_radius: Literal["sharp", "rounded", "pill"] = "rounded"
    button_size: Literal["small", "medium", "large"] = "medium"
    density: Literal["low", "medium", "high"] = "medium"
    typography_weight: Literal["light", "regular", "bold"] = "regular"


class InteractionTraits(BaseModel):
    """Interaction behavior traits from reducer"""
    decision_confidence: Literal["low", "medium", "high"] = "medium"
    exploration_tolerance: Literal["low", "medium", "high"] = "medium"
    scroll_behavior: Literal["slow", "moderate", "fast"] = "moderate"


class BehavioralTraits(BaseModel):
    """Behavioral pattern traits from reducer"""
    speed_vs_accuracy: Literal["speed", "balanced", "accuracy"] = "balanced"
    engagement_depth: Literal["shallow", "moderate", "deep"] = "moderate"


class ReducerOutput(BaseModel):
    """
    Canonical reducer output matching the system spec.
    This is emitted by the preference_reducer after processing agent streams.
    """
    visual: VisualTraits = Field(default_factory=VisualTraits)
    interaction: InteractionTraits = Field(default_factory=InteractionTraits)
    behavioral: BehavioralTraits = Field(default_factory=BehavioralTraits)


class ReducerContext(BaseModel):
    """Context metadata associated with each reducer output"""
    session_id: str
    page_type: str = "home"
    device_type: Literal["desktop", "mobile", "tablet"] = "desktop"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ReducerPayload(BaseModel):
    """Complete reducer payload with context"""
    output: ReducerOutput
    context: ReducerContext


# Convenience factory for default state
def create_default_reducer_output() -> ReducerOutput:
    """Create a neutral default reducer output"""
    return ReducerOutput(
        visual=VisualTraits(),
        interaction=InteractionTraits(),
        behavioral=BehavioralTraits()
    )
