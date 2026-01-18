"""
Feature Schema for Vector-Based Module Matching

Defines the 12-dimensional feature space used to represent both
modules and user profiles for similarity matching.
"""
from typing import List, Dict, Literal
import numpy as np

# Number of dimensions in our feature vector
FEATURE_DIMENSIONS = 12

# Type alias for feature vectors
FeatureVector = List[float]

# Feature index mapping
class FeatureIndex:
    """Indices for each feature in the vector"""
    DARKNESS = 0           # 0=light, 1=dark
    VIBRANCY = 1           # 0=muted, 1=vibrant  
    CORNER_ROUNDNESS = 2   # 0=sharp, 1=pill
    DENSITY = 3            # 0=low, 1=high
    TYPOGRAPHY_WEIGHT = 4  # 0=light, 1=bold
    BUTTON_SIZE = 5        # 0=small, 1=large
    MINIMALISM = 6         # Genre weight
    BRUTALISM = 7          # Genre weight
    GLASS_EFFECT = 8       # Genre weight
    LOUDNESS = 9           # Genre weight (experimental)
    INTERACTIVITY = 10     # Animation level
    EXPLORATION = 11       # Novel vs stable preference


# Encoding mappings for categorical values
ENCODINGS = {
    # Color scheme: darkness level
    "color_scheme": {
        "light": 0.0,
        "dark": 1.0,
        "vibrant": 0.5,
    },
    # Corner radius: roundness level
    "corner_radius": {
        "sharp": 0.0,
        "rounded": 0.5,
        "pill": 1.0,
    },
    # Density level
    "density": {
        "low": 0.0,
        "medium": 0.5,
        "high": 1.0,
    },
    # Typography weight
    "typography_weight": {
        "light": 0.0,
        "regular": 0.5,
        "bold": 1.0,
    },
    # Button size
    "button_size": {
        "small": 0.0,
        "medium": 0.5,
        "large": 1.0,
    },
    # Decision confidence → exploration
    "decision_confidence": {
        "high": 0.2,    # Confident = less exploration
        "medium": 0.5,
        "low": 0.8,     # Uncertain = more exploration
    },
    # Exploration tolerance
    "exploration_tolerance": {
        "low": 0.2,
        "medium": 0.5,
        "high": 0.8,
    },
    # Engagement depth → interactivity preference
    "engagement_depth": {
        "shallow": 0.2,
        "moderate": 0.5,
        "deep": 0.8,
    },
}

# Genre to vector component mapping
GENRE_VECTORS = {
    "base": [0.0, 0.0, 0.0, 0.2],      # minimalism, brutalism, glass, loudness
    "minimalist": [1.0, 0.0, 0.0, 0.0],
    "neobrutalist": [0.0, 1.0, 0.0, 0.3],
    "glassmorphism": [0.3, 0.0, 1.0, 0.0],
    "loud": [0.0, 0.2, 0.0, 1.0],
    "cyber": [0.2, 0.3, 0.2, 0.5],
}


def encode_value(category: str, value: str) -> float:
    """Encode a categorical value to a float in [0, 1]"""
    if category in ENCODINGS and value in ENCODINGS[category]:
        return ENCODINGS[category][value]
    return 0.5  # Default to neutral


def create_zero_vector() -> FeatureVector:
    """Create a zero/neutral feature vector"""
    return [0.5] * FEATURE_DIMENSIONS


def normalize_vector(vector: FeatureVector) -> FeatureVector:
    """Normalize vector to unit length for cosine similarity"""
    arr = np.array(vector)
    norm = np.linalg.norm(arr)
    if norm > 0:
        return (arr / norm).tolist()
    return vector
