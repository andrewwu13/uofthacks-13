"""
User preference models
"""

from pydantic import BaseModel
from typing import Optional, List


class GenreWeights(BaseModel):
    """Probability weights for each UI genre"""

    glassmorphism: float = 0.167
    brutalism: float = 0.167
    neumorphism: float = 0.167
    cyberpunk: float = 0.167
    minimalist: float = 0.167
    monoprint: float = 0.167


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
