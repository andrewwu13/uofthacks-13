"""
Constraint models for component filtering and ranking
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal


class HardConstraints(BaseModel):
    """
    Hard constraints that MUST be satisfied.
    Components not matching these are filtered out entirely.
    """
    color_scheme: Optional[Literal["dark", "light", "vibrant"]] = None
    density: Optional[Literal["low", "medium", "high"]] = None
    device_type: Optional[Literal["desktop", "mobile", "tablet"]] = None
    page_type: Optional[str] = None
    
    # Exclusion list - components to never show
    excluded_component_ids: List[str] = Field(default_factory=list)


class SoftPreferences(BaseModel):
    """
    Soft preferences for ranking components.
    Higher weights = stronger preference.
    """
    corner_radius: Dict[str, float] = Field(
        default_factory=lambda: {"sharp": 0.33, "rounded": 0.34, "pill": 0.33}
    )
    typography_weight: Dict[str, float] = Field(
        default_factory=lambda: {"light": 0.33, "regular": 0.34, "bold": 0.33}
    )
    button_size: Dict[str, float] = Field(
        default_factory=lambda: {"small": 0.33, "medium": 0.34, "large": 0.33}
    )
    
    # Genre preferences (minimalist, neobrutalist, glassmorphism, etc.)
    genre_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "base": 0.4,
            "minimalist": 0.15,
            "neobrutalist": 0.15,
            "glassmorphism": 0.15,
            "loud": 0.15
        }
    )


class Constraints(BaseModel):
    """Combined constraints for component selection"""
    hard: HardConstraints = Field(default_factory=HardConstraints)
    soft: SoftPreferences = Field(default_factory=SoftPreferences)
    exploration_budget: float = Field(default=0.3, ge=0.0, le=1.0)


class ComponentCandidate(BaseModel):
    """A candidate component from vector search or catalog"""
    component_id: str
    component_type: str  # e.g., "hero", "product-grid", "cta"
    genre: str  # e.g., "minimalist", "neobrutalist"
    variant: str  # e.g., "v1", "soft_v3"
    
    # Matching scores
    constraint_score: float = 0.0  # How well it matches hard constraints
    preference_score: float = 0.0  # How well it matches soft preferences
    semantic_score: float = 0.0  # From vector similarity
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    supports_dark_mode: bool = True
    supports_mobile: bool = True


class SelectionResult(BaseModel):
    """Result of component selection process"""
    selected_components: List[ComponentCandidate]
    exploration_components: List[ComponentCandidate]  # "Loud" test components
    total_candidates_considered: int
    selection_timestamp: float
