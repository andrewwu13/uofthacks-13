"""
Pydantic models for the User Profile JSON schema.
Used for vectorization and module matching.
"""
from pydantic import BaseModel
from typing import Literal, Optional


class VisualPreferences(BaseModel):
    """Visual style preferences derived from user behavior"""
    color_scheme: Literal["dark", "light", "vibrant"] = "light"
    corner_radius: Literal["sharp", "rounded", "pill"] = "rounded"
    button_size: Literal["small", "medium", "large"] = "medium"
    density: Literal["low", "medium", "high"] = "medium"
    typography_weight: Literal["light", "regular", "bold"] = "regular"


class InteractionPreferences(BaseModel):
    """Interaction style preferences derived from motor state"""
    decision_confidence: Literal["low", "medium", "high"] = "medium"
    exploration_tolerance: Literal["low", "medium", "high"] = "medium"
    scroll_behavior: Literal["slow", "moderate", "fast"] = "moderate"


class BehavioralPreferences(BaseModel):
    """Behavioral preferences derived from engagement patterns"""
    speed_vs_accuracy: Literal["speed", "balanced", "accuracy"] = "balanced"
    engagement_depth: Literal["shallow", "moderate", "deep"] = "moderate"


class InferredProfile(BaseModel):
    """
    Rich semantic profile inferred by LLM from raw metrics.
    Adds human-readable "vibe" and narrative context.
    """
    summary: str = "New User"
    habits: list[str] = []
    visual_keywords: list[str] = []


class UserProfile(BaseModel):
    """
    Complete user profile for vectorization.
    This JSON will be embedded and used to query the module vector database.
    """
    visual: VisualPreferences = VisualPreferences()
    interaction: InteractionPreferences = InteractionPreferences()
    behavioral: BehavioralPreferences = BehavioralPreferences()
    inferred: InferredProfile = InferredProfile()
    
    def to_vector_key(self) -> str:
        """Convert profile to a string suitable for embedding"""
        parts = []
        # Add visual preference tokens
        parts.append(f"color:{self.visual.color_scheme}")
        parts.append(f"corners:{self.visual.corner_radius}")
        parts.append(f"buttons:{self.visual.button_size}")
        parts.append(f"density:{self.visual.density}")
        parts.append(f"typography:{self.visual.typography_weight}")
        
        # Add interaction preference tokens
        parts.append(f"confidence:{self.interaction.decision_confidence}")
        parts.append(f"exploration:{self.interaction.exploration_tolerance}")
        parts.append(f"scroll:{self.interaction.scroll_behavior}")
        
        # Add behavioral tokens
        parts.append(f"speed_accuracy:{self.behavioral.speed_vs_accuracy}")
        parts.append(f"depth:{self.behavioral.engagement_depth}")
        
        # Add semantic keywords (crucial for "vibe" matching)
        parts.extend(self.inferred.visual_keywords)
        parts.append(f"persona:{self.inferred.summary}")
        
        return " ".join(parts)
