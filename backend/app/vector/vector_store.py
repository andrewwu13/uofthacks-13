"""
Vector Store - In-memory vector database with cosine similarity search

Provides fast nearest-neighbor search for module matching without
external dependencies.
"""
import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from app.vector.feature_schema import FeatureVector, FEATURE_DIMENSIONS


@dataclass
class SearchResult:
    """Result from vector similarity search"""
    id: str
    score: float  # Cosine similarity (higher = more similar)
    vector: FeatureVector


class VectorStore:
    """
    In-memory vector store with cosine similarity search.
    
    Optimized for small catalogs (~100-1000 vectors) where
    O(n) search is acceptable.
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
    
    def add_batch(self, items: List[Tuple[str, FeatureVector, dict]]):
        """Add multiple vectors at once"""
        for id, vector, metadata in items:
            self.add(id, vector, metadata)
    
    def remove(self, id: str):
        """Remove a vector from the store"""
        if id in self.vectors:
            del self.vectors[id]
            del self.metadata[id]
    
    def get(self, id: str) -> Optional[FeatureVector]:
        """Get vector by ID"""
        if id in self.vectors:
            return self.vectors[id].tolist()
        return None
    
    def search(
        self, 
        query: FeatureVector, 
        top_k: int = 5,
        filter_fn: callable = None
    ) -> List[SearchResult]:
        """
        Find top-k most similar vectors using cosine similarity.
        
        Args:
            query: Query feature vector
            top_k: Number of results to return
            filter_fn: Optional filter function (id, metadata) -> bool
            
        Returns:
            List of SearchResult ordered by similarity (descending)
        """
        if not self.vectors:
            return []
        
        # Normalize query vector
        query_arr = np.array(query, dtype=np.float32)
        query_norm = np.linalg.norm(query_arr)
        if query_norm > 0:
            query_arr = query_arr / query_norm
        
        # Compute similarities
        results = []
        for id, vec in self.vectors.items():
            # Optional filter
            if filter_fn and not filter_fn(id, self.metadata.get(id, {})):
                continue
            
            # Cosine similarity (dot product of normalized vectors)
            similarity = float(np.dot(query_arr, vec))
            results.append(SearchResult(
                id=id,
                score=similarity,
                vector=vec.tolist()
            ))
        
        # Sort by similarity (descending)
        results.sort(key=lambda r: r.score, reverse=True)
        
        return results[:top_k]
    
    def search_by_type(
        self,
        query: FeatureVector,
        module_type: str,
        top_k: int = 3
    ) -> List[SearchResult]:
        """
        Search for similar vectors filtering by module type.
        
        Args:
            query: Query feature vector
            module_type: Module type to filter by (hero, cta, etc.)
            top_k: Number of results per type
        """
        def type_filter(id: str, metadata: dict) -> bool:
            return metadata.get("module_type") == module_type
        
        return self.search(query, top_k=top_k, filter_fn=type_filter)
    
    def __len__(self) -> int:
        return len(self.vectors)
    
    def clear(self):
        """Clear all vectors"""
        self.vectors.clear()
        self.metadata.clear()


# Global vector store instance
vector_store = VectorStore()



def initialize_vector_store():
    """
    Initialize the global vector store with module catalog.
    Called on app startup.
    """
    from app.vector.module_vectors import MODULE_CATALOG, module_to_vector
    
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
            }
        )
    
    print(f"[VectorStore] Initialized with {len(vector_store)} modules")


def search_similar_modules(
    profile_vector: FeatureVector,
    module_types: List[str] = None,
    top_k: int = 5
) -> Dict[str, List[SearchResult]]:
    """
    Search for similar modules.
    
    Args:
        profile_vector: User profile feature vector
        module_types: Legacy arg, ignored (or preserved for compat). 
                      We now return a 'recommended' list.
        top_k: Results to return
        
    Returns:
        Dict with 'recommended' key containing SearchResults
    """
    # Simply search the entire store, as all modules are now Product Modules
    # but with different layouts/genres.
    results = vector_store.search(
        query=profile_vector,
        top_k=top_k
    )
    
    return {"recommended": results}
