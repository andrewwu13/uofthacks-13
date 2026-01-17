"""
User preference models
"""
from pydantic import BaseModel
from typing import Optional, List


class GenreWeights(BaseModel):
    """Probability weights for each UI genre"""
    base: float = 0.2
    minimalist: float = 0.2
    neobrutalist: float = 0.2
    glassmorphism: float = 0.2
    loud: float = 0.2


class ColorPreferences(BaseModel):
    """Learned color preferences"""
    primary_colors: List[str] = []
    accent_colors: List[str] = []
    preferred_contrast: str = "normal"  # "low", "normal", "high"


class UserPreferences(BaseModel):
    """Aggregated user preferences"""
    session_id: str
    genre_weights: GenreWeights = GenreWeights()
    color_preferences: ColorPreferences = ColorPreferences()
    preferred_font_weight: Optional[int] = None
    preferred_border_radius: Optional[int] = None
    interaction_confidence: float = 0.0  # 0-1, how confident we are in preferences
    total_interactions: int = 0
