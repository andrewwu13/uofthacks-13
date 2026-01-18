"""
Vector Module Exports

Provides vector-based similarity search for matching user profiles
to UI modules in a shared 12-dimensional feature space.
"""

from app.vector.feature_schema import (
    FEATURE_DIMENSIONS,
    FeatureVector,
    FeatureIndex,
    encode_value,
    normalize_vector,
    create_zero_vector,
    GENRE_VECTORS,
    ENCODINGS,
)

from app.vector.module_vectors import (
    ModuleMetadata,
    MODULE_CATALOG,
    module_to_vector,
    get_module_by_id,
    get_modules_by_type,
)

from app.vector.profile_vectors import (
    profile_to_vector,
    traits_to_vector,
)

from app.vector.vector_store import (
    VectorStore,
    SearchResult,
    vector_store,
    initialize_vector_store,
    search_similar_modules,
)

__all__ = [
    # Schema
    "FEATURE_DIMENSIONS",
    "FeatureVector", 
    "FeatureIndex",
    "encode_value",
    "normalize_vector",
    "create_zero_vector",
    "GENRE_VECTORS",
    "ENCODINGS",
    # Modules
    "ModuleMetadata",
    "MODULE_CATALOG",
    "module_to_vector",
    "get_module_by_id",
    "get_modules_by_type",
    # Profiles
    "profile_to_vector",
    "traits_to_vector",
    # Store
    "VectorStore",
    "SearchResult",
    "vector_store",
    "initialize_vector_store",
    "search_similar_modules",
]
