"""
Vector Module Exports

Provides vector-based similarity search for matching user profiles
to UI modules using semantic text embeddings.
"""

from app.vector.feature_schema import (
    FEATURE_DIMENSIONS,
    FeatureVector,
    normalize_vector,
)

from app.vector.module_vectors import (
    ModuleMetadata,
    MODULE_CATALOG,
    module_to_vector,
    get_module_by_id,
    get_modules_by_type,
    initialize_module_vectors_async,
)

from app.vector.profile_vectors import (
    user_profile_to_vector_async,
    get_recommended_genre_async,
    get_recommended_template_id_async,
)

from app.vector.vector_store import (
    VectorStore,
    SearchResult,
    vector_store,
    initialize_vector_store_async,
    search_similar_modules,
)

__all__ = [
    # Schema
    "FEATURE_DIMENSIONS",
    "FeatureVector",
    "normalize_vector",
    # Modules
    "ModuleMetadata",
    "MODULE_CATALOG",
    "module_to_vector",
    "get_module_by_id",
    "get_modules_by_type",
    "initialize_module_vectors_async",
    # Profiles
    "user_profile_to_vector_async",
    "get_recommended_genre_async",
    "get_recommended_template_id_async",
    # Store
    "VectorStore",
    "SearchResult",
    "vector_store",
    "initialize_vector_store_async",
    "search_similar_modules",
]
