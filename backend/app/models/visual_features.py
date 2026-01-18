"""
Visual Features for Module Vectorization

Each module template has a numerical feature vector describing its visual properties.
These values (0.0 - 1.0) enable ML-based recommendations and similarity calculations.

11 Dimensions:
- genre_id: Genre index normalized (0.0 - 1.0)
- curvature: Border radius / roundness
- contrast: Text/background contrast level
- color_warmth: Cool ↔ Warm color temperature
- color_saturation: Muted ↔ Vibrant colors
- motion_intensity: Animation/glow effects
- visual_density: Sparse ↔ Dense layout
- border_weight: Border thickness
- font_weight: Light ↔ Bold typography
- animation_duration: Short ↔ Long animations
- shadow_depth: No shadow ↔ Deep shadow
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import List, Dict, Optional
import math

# ============================================
# GENRE DEFINITIONS
# ============================================

class Genre(IntEnum):
    BASE = 0
    MINIMALIST = 1
    NEOBRUTALIST = 2
    GLASSMORPHISM = 3
    LOUD = 4
    CYBER = 5

GENRE_NAMES: Dict[Genre, str] = {
    Genre.BASE: "Base",
    Genre.MINIMALIST: "Minimalist",
    Genre.NEOBRUTALIST: "Neobrutalist",
    Genre.GLASSMORPHISM: "Glassmorphism",
    Genre.LOUD: "Loud",
    Genre.CYBER: "Cyber",
}

# ============================================
# VISUAL FEATURE VECTOR
# ============================================

@dataclass
class VisualFeatureVector:
    """Numerical representation of a module's visual properties."""
    
    # Identification
    genre_id: float           # 0.0 - 1.0 (genre / 5)
    genre_name: str           # Human-readable genre name
    
    # Core Visual Properties (0.0 - 1.0)
    curvature: float          # Border radius: 0 = sharp, 1 = very rounded
    contrast: float           # Text/BG contrast: 0 = low, 1 = high
    color_warmth: float       # 0 = cool/cyber, 1 = warm/loud
    color_saturation: float   # 0 = muted, 1 = vibrant
    motion_intensity: float   # 0 = static, 1 = animated/glowing
    visual_density: float     # 0 = sparse/minimal, 1 = dense
    border_weight: float      # 0 = none/thin, 1 = thick brutalist
    
    # Extended Properties
    font_weight: float        # 0 = light, 1 = heavy/bold
    animation_duration: float # 0 = instant, 1 = long/slow
    shadow_depth: float       # 0 = flat/no shadow, 1 = deep shadow
    
    def to_array(self) -> List[float]:
        """Convert to numerical array for ML."""
        return [
            self.genre_id,
            self.curvature,
            self.contrast,
            self.color_warmth,
            self.color_saturation,
            self.motion_intensity,
            self.visual_density,
            self.border_weight,
            self.font_weight,
            self.animation_duration,
            self.shadow_depth,
        ]
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for API response."""
        return {
            "genre_id": self.genre_id,
            "genre_name": self.genre_name,
            "curvature": self.curvature,
            "contrast": self.contrast,
            "color_warmth": self.color_warmth,
            "color_saturation": self.color_saturation,
            "motion_intensity": self.motion_intensity,
            "visual_density": self.visual_density,
            "border_weight": self.border_weight,
            "font_weight": self.font_weight,
            "animation_duration": self.animation_duration,
            "shadow_depth": self.shadow_depth,
        }

# ============================================
# GENRE VISUAL PROFILES
# ============================================

# Predefined visual profiles for each genre (derived from CSS)
GENRE_VISUAL_PROFILES: Dict[Genre, Dict[str, float]] = {
    # GENRE 0: BASE - Clean, professional dark UI
    Genre.BASE: {
        "curvature": 0.5,          # 12px radius - moderate
        "contrast": 0.6,           # Good contrast on dark
        "color_warmth": 0.4,       # Slightly cool (blue accent)
        "color_saturation": 0.4,   # Moderate saturation
        "motion_intensity": 0.1,   # Minimal animation
        "visual_density": 0.5,     # Balanced density
        "border_weight": 0.2,      # Thin borders
        "font_weight": 0.5,        # Medium weight
        "animation_duration": 0.3, # Standard transitions
        "shadow_depth": 0.3,       # Subtle shadows
    },
    
    # GENRE 1: MINIMALIST - Stark, high contrast, Swiss-inspired
    Genre.MINIMALIST: {
        "curvature": 0.0,          # 0px radius - sharp corners
        "contrast": 1.0,           # Maximum contrast (black/white)
        "color_warmth": 0.3,       # Cool, neutral
        "color_saturation": 0.0,   # No color, monochrome
        "motion_intensity": 0.0,   # No animation
        "visual_density": 0.2,     # Very sparse
        "border_weight": 0.2,      # Thin, precise borders
        "font_weight": 0.4,        # Light to medium
        "animation_duration": 0.0, # No animations
        "shadow_depth": 0.0,       # Flat, no shadow
    },
    
    # GENRE 2: NEOBRUTALIST - Bold, raw, playful chaos
    Genre.NEOBRUTALIST: {
        "curvature": 0.0,          # 0px radius - sharp corners
        "contrast": 0.9,           # High contrast (yellow/black)
        "color_warmth": 0.7,       # Warm yellow
        "color_saturation": 1.0,   # Maximum saturation
        "motion_intensity": 0.2,   # Subtle hover effects
        "visual_density": 0.7,     # Dense, chunky
        "border_weight": 1.0,      # Thick 4px borders
        "font_weight": 0.9,        # Heavy, bold
        "animation_duration": 0.2, # Quick, snappy
        "shadow_depth": 0.8,       # Hard offset shadows
    },
    
    # GENRE 3: GLASSMORPHISM - Ethereal, translucent, dreamy
    Genre.GLASSMORPHISM: {
        "curvature": 1.0,          # 20px radius - very rounded
        "contrast": 0.4,           # Low contrast (translucent)
        "color_warmth": 0.5,       # Neutral with purple accent
        "color_saturation": 0.5,   # Moderate pastels
        "motion_intensity": 0.4,   # Subtle blur effects
        "visual_density": 0.4,     # Light, airy
        "border_weight": 0.1,      # Very thin, glassy
        "font_weight": 0.4,        # Light weight
        "animation_duration": 0.6, # Smooth, elegant
        "shadow_depth": 0.5,       # Soft glow shadows
    },
    
    # GENRE 4: LOUD - Attention-grabbing, gradient, energetic
    Genre.LOUD: {
        "curvature": 0.9,          # 24px radius - very rounded
        "contrast": 0.7,           # Good contrast on gradient
        "color_warmth": 1.0,       # Maximum warm (orange/red)
        "color_saturation": 0.9,   # High saturation
        "motion_intensity": 0.5,   # Pulse animations
        "visual_density": 0.6,     # Moderately dense
        "border_weight": 0.0,      # No borders, gradients
        "font_weight": 0.8,        # Bold, impactful
        "animation_duration": 0.5, # Medium pulse duration
        "shadow_depth": 0.7,       # Dramatic colored shadows
    },
    
    # GENRE 5: CYBER - Matrix, terminal, hacker aesthetic
    Genre.CYBER: {
        "curvature": 0.1,          # 4px radius - nearly sharp
        "contrast": 0.8,           # High (green on black)
        "color_warmth": 0.0,       # Maximum cool (green)
        "color_saturation": 0.7,   # Neon green saturation
        "motion_intensity": 0.8,   # Glow/flicker animations
        "visual_density": 0.5,     # Data-like density
        "border_weight": 0.3,      # Dashed terminal borders
        "font_weight": 0.5,        # Monospace medium
        "animation_duration": 0.9, # Slow glow cycles
        "shadow_depth": 0.4,       # Neon glow effect
    },
}

# ============================================
# UTILITY FUNCTIONS
# ============================================

def get_visual_feature_vector(genre: Genre) -> VisualFeatureVector:
    """Get the complete visual feature vector for a genre."""
    profile = GENRE_VISUAL_PROFILES[genre]
    
    return VisualFeatureVector(
        genre_id=genre / 5,  # Normalize to 0.0 - 1.0
        genre_name=GENRE_NAMES[genre],
        **profile
    )


def get_all_visual_feature_vectors() -> List[VisualFeatureVector]:
    """Get all visual feature vectors as a list."""
    return [get_visual_feature_vector(genre) for genre in Genre]


def vector_distance(a: VisualFeatureVector, b: VisualFeatureVector) -> float:
    """
    Calculate Euclidean distance between two visual feature vectors.
    Lower distance = more similar.
    """
    arr_a = a.to_array()
    arr_b = b.to_array()
    
    sum_squares = sum((x - y) ** 2 for x, y in zip(arr_a, arr_b))
    return math.sqrt(sum_squares)


def cosine_similarity(a: VisualFeatureVector, b: VisualFeatureVector) -> float:
    """
    Calculate cosine similarity between two visual feature vectors.
    Returns: -1 to 1 (1 = identical direction)
    """
    arr_a = a.to_array()
    arr_b = b.to_array()
    
    dot_product = sum(x * y for x, y in zip(arr_a, arr_b))
    mag_a = math.sqrt(sum(x ** 2 for x in arr_a))
    mag_b = math.sqrt(sum(x ** 2 for x in arr_b))
    
    magnitude = mag_a * mag_b
    return dot_product / magnitude if magnitude != 0 else 0


def find_most_similar_genre(preference_vector: List[float]) -> Genre:
    """Find the most similar genre to a given preference vector."""
    best_genre = Genre.BASE
    best_similarity = float("-inf")
    
    for genre in Genre:
        genre_vector = get_visual_feature_vector(genre)
        genre_array = genre_vector.to_array()
        
        # Calculate cosine similarity
        dot_product = sum(p * g for p, g in zip(preference_vector, genre_array))
        mag_pref = math.sqrt(sum(p ** 2 for p in preference_vector))
        mag_genre = math.sqrt(sum(g ** 2 for g in genre_array))
        
        similarity = dot_product / (mag_pref * mag_genre) if (mag_pref * mag_genre) != 0 else 0
        
        if similarity > best_similarity:
            best_similarity = similarity
            best_genre = genre
    
    return best_genre


# ============================================
# FEATURE DIMENSION METADATA
# ============================================

FEATURE_DIMENSIONS = [
    {"key": "genre_id", "label": "Genre", "description": "Normalized genre index (0-5)"},
    {"key": "curvature", "label": "Curvature", "description": "Border radius / roundness"},
    {"key": "contrast", "label": "Contrast", "description": "Text/background contrast level"},
    {"key": "color_warmth", "label": "Color Warmth", "description": "Cool ↔ Warm temperature"},
    {"key": "color_saturation", "label": "Saturation", "description": "Muted ↔ Vibrant colors"},
    {"key": "motion_intensity", "label": "Motion", "description": "Animation intensity"},
    {"key": "visual_density", "label": "Density", "description": "Sparse ↔ Dense layout"},
    {"key": "border_weight", "label": "Border", "description": "Border thickness"},
    {"key": "font_weight", "label": "Font Weight", "description": "Light ↔ Bold typography"},
    {"key": "animation_duration", "label": "Animation Duration", "description": "Short ↔ Long animations"},
    {"key": "shadow_depth", "label": "Shadow Depth", "description": "Flat ↔ Deep shadow"},
]
