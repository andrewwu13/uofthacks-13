"""
Profile Vectors - Convert user profiles (ReducerOutput) to feature vectors

Maps user preferences and behavioral traits to the same 12-dimensional
feature space as modules for similarity matching.
"""
from typing import List
from app.models.reducer import ReducerOutput, VisualTraits, InteractionTraits, BehavioralTraits
from app.vector.feature_schema import (
    FEATURE_DIMENSIONS,
    FeatureVector,
    FeatureIndex,
    encode_value,
    normalize_vector,
)


def profile_to_vector(profile: ReducerOutput) -> FeatureVector:
    """
    Convert a ReducerOutput (user profile) to a normalized feature vector.
    
    This allows us to find modules that are similar to the user's preferences
    using cosine similarity in the shared feature space.
    """
    vector = [0.0] * FEATURE_DIMENSIONS
    
    visual = profile.visual
    interaction = profile.interaction
    behavioral = profile.behavioral
    
    # ========================================
    # Visual Traits → Feature Vector
    # ========================================
    
    # Color scheme → darkness & vibrancy
    if visual.color_scheme == "dark":
        vector[FeatureIndex.DARKNESS] = 1.0
        vector[FeatureIndex.VIBRANCY] = 0.4
    elif visual.color_scheme == "vibrant":
        vector[FeatureIndex.DARKNESS] = 0.3
        vector[FeatureIndex.VIBRANCY] = 1.0
    else:  # light
        vector[FeatureIndex.DARKNESS] = 0.0
        vector[FeatureIndex.VIBRANCY] = 0.3
    
    # Corner radius
    vector[FeatureIndex.CORNER_ROUNDNESS] = encode_value("corner_radius", visual.corner_radius)
    
    # Density
    vector[FeatureIndex.DENSITY] = encode_value("density", visual.density)
    
    # Typography weight
    vector[FeatureIndex.TYPOGRAPHY_WEIGHT] = encode_value("typography_weight", visual.typography_weight)
    
    # Button size
    vector[FeatureIndex.BUTTON_SIZE] = encode_value("button_size", visual.button_size)
    
    # ========================================
    # Genre Inference from Visual/Behavioral
    # ========================================
    
    # Infer genre preferences from visual traits
    # Low density + light weight → minimalist
    minimalism_score = (1.0 - vector[FeatureIndex.DENSITY]) * 0.5 + \
                       (1.0 - vector[FeatureIndex.TYPOGRAPHY_WEIGHT]) * 0.3 + \
                       (1.0 - vector[FeatureIndex.CORNER_ROUNDNESS]) * 0.2
    
    # High contrast + bold + sharp → brutalist
    brutalism_score = vector[FeatureIndex.VIBRANCY] * 0.4 + \
                      vector[FeatureIndex.TYPOGRAPHY_WEIGHT] * 0.4 + \
                      (1.0 - vector[FeatureIndex.CORNER_ROUNDNESS]) * 0.2
    
    # Rounded + medium density + blur-friendly → glass
    # Note: Clamp the density term to prevent negative values
    glass_score = vector[FeatureIndex.CORNER_ROUNDNESS] * 0.5 + \
                  max(0.0, 1.0 - abs(vector[FeatureIndex.DENSITY] - 0.5) * 2) * 0.3 + \
                  vector[FeatureIndex.DARKNESS] * 0.2
    
    # High vibrancy + large buttons + exploration → loud
    exploration_factor = encode_value("exploration_tolerance", interaction.exploration_tolerance)
    loudness_score = vector[FeatureIndex.VIBRANCY] * 0.4 + \
                     vector[FeatureIndex.BUTTON_SIZE] * 0.3 + \
                     exploration_factor * 0.3
    
    # Clamp all scores to [0.0, 1.0]
    vector[FeatureIndex.MINIMALISM] = max(0.0, min(1.0, minimalism_score))
    vector[FeatureIndex.BRUTALISM] = max(0.0, min(1.0, brutalism_score))
    vector[FeatureIndex.GLASS_EFFECT] = max(0.0, min(1.0, glass_score))
    vector[FeatureIndex.LOUDNESS] = max(0.0, min(1.0, loudness_score))
    
    # ========================================
    # Behavioral Traits → Interactivity & Exploration
    # ========================================
    
    # Engagement depth → interactivity preference
    vector[FeatureIndex.INTERACTIVITY] = encode_value("engagement_depth", behavioral.engagement_depth)
    
    # Exploration tolerance
    vector[FeatureIndex.EXPLORATION] = exploration_factor
    
    return normalize_vector(vector)


def traits_to_vector(
    visual: VisualTraits = None,
    interaction: InteractionTraits = None,
    behavioral: BehavioralTraits = None
) -> FeatureVector:
    """
    Convert individual traits to feature vector.
    Useful when you have partial trait information.
    """
    profile = ReducerOutput(
        visual=visual or VisualTraits(),
        interaction=interaction or InteractionTraits(),
        behavioral=behavioral or BehavioralTraits()
    )
    return profile_to_vector(profile)
