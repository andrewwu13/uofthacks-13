"""
Semantic cache for LLM calls
Uses embedding-based cache with cosine similarity
"""
import hashlib
from typing import Optional, Tuple
import numpy as np


class SemanticCache:
    """
    Embedding-based cache for LLM responses.
    Before calling LLM, embed prompt summary and check for similar cached responses.
    Uses cosine similarity threshold to determine cache hit.
    """
    
    def __init__(self, similarity_threshold: float = 0.92):
        self.threshold = similarity_threshold
        self.cache: dict = {}  # {hash: (embedding, response)}
        self.embedding_model = None  # TODO: Initialize embedding model
    
    async def get(self, prompt_summary: str) -> Optional[str]:
        """
        Check cache for similar prompt.
        Returns cached response if similarity > threshold.
        """
        if not self.cache:
            return None
        
        # Get embedding for prompt
        embedding = await self._embed(prompt_summary)
        
        # Find most similar cached entry
        best_match, best_similarity = self._find_similar(embedding)
        
        if best_similarity >= self.threshold:
            return best_match
        
        return None
    
    async def set(self, prompt_summary: str, response: str):
        """Store prompt-response pair with embedding"""
        embedding = await self._embed(prompt_summary)
        cache_key = self._hash(prompt_summary)
        self.cache[cache_key] = (embedding, response)
    
    async def _embed(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        # TODO: Use actual embedding model
        # For now, return random embedding for placeholder
        return np.random.rand(1536)
    
    def _find_similar(self, embedding: np.ndarray) -> Tuple[Optional[str], float]:
        """Find most similar cached entry"""
        best_response = None
        best_similarity = 0.0
        
        for _, (cached_embedding, response) in self.cache.items():
            similarity = self._cosine_similarity(embedding, cached_embedding)
            if similarity > best_similarity:
                best_similarity = similarity
                best_response = response
        
        return best_response, best_similarity
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    def _hash(self, text: str) -> str:
        """Generate hash for text"""
        return hashlib.md5(text.encode()).hexdigest()


semantic_cache = SemanticCache()
