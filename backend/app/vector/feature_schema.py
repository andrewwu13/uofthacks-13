"""
Feature Schema for Vector-Based Module Matching

Defines the text embedding feature space used to represent both
modules and user profiles for similarity matching.
"""

from typing import List
import numpy as np

# Number of dimensions for OpenRouter text-embedding-3-small
FEATURE_DIMENSIONS = 1536

# Type alias for feature vectors
FeatureVector = List[float]

def normalize_vector(vector: FeatureVector) -> FeatureVector:
    """Normalize vector to unit length for cosine similarity"""
    arr = np.array(vector)
    norm = np.linalg.norm(arr)
    if norm > 0:
        return (arr / norm).tolist()
    return vector
