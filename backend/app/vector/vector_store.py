"""
Vector Store - In-memory vector database with cosine similarity search

Provides fast nearest-neighbor search for module matching using 
text embeddings.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from app.vector.feature_schema import FeatureVector


@dataclass
class SearchResult:
    """Result from vector similarity search"""

    id: str
    score: float  # Cosine similarity (higher = more similar)
    vector: FeatureVector


class VectorStore:
    """
    In-memory vector store with cosine similarity search.
    """

    def __init__(self):
        self.vectors: Dict[int, np.ndarray] = {}
        self.metadata: Dict[int, dict] = {}

    def add(self, id: int, vector: FeatureVector, metadata: dict = None):
        """Add a vector to the store"""
        arr = np.array(vector, dtype=np.float32)
        # Normalize for cosine similarity
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        self.vectors[id] = arr
        self.metadata[id] = metadata or {}

    def get(self, id: str) -> Optional[FeatureVector]:
        """Get vector by ID"""
        if id in self.vectors:
            return self.vectors[id].tolist()
        return None

    def search(
        self, query: FeatureVector, top_k: int = 5, filter_fn: callable = None
    ) -> List[SearchResult]:
        """Find top-k most similar vectors using cosine similarity."""
        if not self.vectors:
            return []

        # Normalize query vector
        query_arr = np.array(query, dtype=np.float32)
        query_norm = np.linalg.norm(query_arr)
        if query_norm > 0:
            query_arr = query_arr / query_norm

        results = []
        for id, vec in self.vectors.items():
            if filter_fn and not filter_fn(id, self.metadata.get(id, {})):
                continue

            similarity = float(np.dot(query_arr, vec))
            results.append(SearchResult(id=id, score=similarity, vector=vec.tolist()))

        # Sort by similarity (descending)
        results.sort(key=lambda r: r.score, reverse=True)

        return results[:top_k]

    def __len__(self) -> int:
        return len(self.vectors)

    def clear(self):
        """Clear all vectors"""
        self.vectors.clear()
        self.metadata.clear()


# Global vector store instance
vector_store = VectorStore()


async def initialize_vector_store_async():
    """
    Initialize the global vector store with module catalog embeddings.
    Called on app startup.
    """
    from app.vector.module_vectors import MODULE_CATALOG, module_to_vector, initialize_module_vectors_async

    # First generate all embeddings
    await initialize_module_vectors_async()

    vector_store.clear()

    for module in MODULE_CATALOG:
        vector = module_to_vector(module)
        vector_store.add(
            id=module.module_id,
            vector=vector,
            metadata={
                "layout": module.layout,
                "genre": module.genre,
                "tags": module.tags,
            },
        )

    print(f"[VectorStore] Initialized with {len(vector_store)} modules")


def search_similar_modules(
    profile_vector: FeatureVector, top_k: int = 5
) -> Dict[str, List[SearchResult]]:
    """
    Search for similar modules. Returns a dict with 'recommended' key.
    """
    results = vector_store.search(query=profile_vector, top_k=top_k)
    return {"recommended": results}
