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


# ============================================
# UserProfile Direct Conversion (Simplified Flow)
# ============================================

def user_profile_to_vector(profile_dict: dict) -> FeatureVector:
    """
    Convert a UserProfile dict directly to a feature vector.
    Skips the ReducerOutput intermediate step.
    
    Args:
        profile_dict: Dict with 'visual', 'interaction', 'behavioral' keys
        
    Returns:
        Normalized 12-dimension feature vector
    """
    # Extract traits, using defaults if missing
    visual = profile_dict.get('visual', {})
    interaction = profile_dict.get('interaction', {})
    behavioral = profile_dict.get('behavioral', {})
    
    # Create ReducerOutput internally (same underlying conversion)
    reducer = ReducerOutput(
        visual=VisualTraits(**visual) if visual else VisualTraits(),
        interaction=InteractionTraits(**interaction) if interaction else InteractionTraits(),
        behavioral=BehavioralTraits(**behavioral) if behavioral else BehavioralTraits(),
    )
    
    return profile_to_vector(reducer)


def get_recommended_genre(profile_dict: dict) -> str:
    """
    Get the recommended genre for a user profile by querying the vector store.
    
    Args:
        profile_dict: UserProfile dict from agents
        
    Returns:
        Genre name (e.g., "loud", "minimalist", "glassmorphism")
    """
    from app.vector.vector_store import search_similar_modules
    
    # Convert profile to vector
    profile_vec = user_profile_to_vector(profile_dict)
    
    # Query vector store for similar modules
    results = search_similar_modules(profile_vec, module_types=["hero"])
    
    # Get genre from top hero match
    hero_results = results.get("hero", [])
    if hero_results:
        top_result = hero_results[0]
        # Get genre from vector store metadata
        from app.vector.vector_store import vector_store
        metadata = vector_store.metadata.get(top_result.id, {})
        return metadata.get("genre", "base")
    
    return "base"  # Fallback


def get_recommended_template_id(profile_dict: dict) -> int:
    """
    Get the recommended integer Template ID for a user profile.
    Searches for the best matching 'product-grid' module (Type 0).
    
    Args:
        profile_dict: UserProfile dict
        
    Returns:
        int: Module ID (0-35)
    """
    from app.vector.vector_store import search_similar_modules
    
    # Convert profile to vector
    profile_vec = user_profile_to_vector(profile_dict)
    
    # Query vector store for similar modules (specifically product-grids which map to cards)
    results = search_similar_modules(profile_vec, module_types=["product-grid"])
    
    # Get top match
    grid_results = results.get("product-grid", [])
    if grid_results:
        top_result = grid_results[0]
        # The ID is now an integer
        return top_result.id
    
    # Fallback to ID 0 (Base Product Card)
    return 0

