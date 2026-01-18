"""
Semantic cache for LLM calls using Gemini embeddings.
Uses embedding-based cache with cosine similarity for token cost optimization.
Stores cache in Redis for persistence across restarts.
"""
import hashlib
import json
import logging
from typing import Optional, Tuple, Dict, Any
import numpy as np

logger = logging.getLogger(__name__)


class SemanticCache:
    """
    Embedding-based cache for LLM responses using Gemini embeddings.
    Before calling LLM, embed prompt summary and check for similar cached responses.
    Uses cosine similarity threshold to determine cache hit.
    
    Cache entries are stored in Redis with format:
    - Key: semantic_cache:{hash}
    - Value: JSON {embedding: [...], result: {...}, created_at: timestamp}
    """
    
    def __init__(
        self,
        similarity_threshold: float = 0.92,
        cache_ttl_seconds: int = 3600,
        redis_client=None
    ):
        self.threshold = similarity_threshold
        self.ttl = cache_ttl_seconds
        self.redis = redis_client
        self.embeddings_model = None
        self._initialized = False
        
        # In-memory cache fallback (when Redis unavailable)
        self._memory_cache: Dict[str, Tuple[np.ndarray, Any]] = {}
    
    async def initialize(self, google_api_key: str):
        """Initialize the Gemini embeddings model."""
        if self._initialized:
            return
        
        if not google_api_key:
            logger.warning("GOOGLE_API_KEY not set. Semantic cache will be disabled.")
            return
        
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            
            # Use text-embedding-004 (free tier, 768 dimensions)
            self.embeddings_model = GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=google_api_key,
            )
            self._initialized = True
            logger.info("Semantic cache initialized with Gemini text-embedding-004")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini embeddings: {e}")
            self.embeddings_model = None
    
    def is_enabled(self) -> bool:
        """Check if semantic cache is ready to use."""
        return self._initialized and self.embeddings_model is not None
    
    async def get(self, summary: str) -> Optional[Dict[str, Any]]:
        """
        Check cache for similar prompt.
        Returns cached result if similarity > threshold.
        
        Args:
            summary: Normalized telemetry summary string
            
        Returns:
            Cached result dict if found, None otherwise
        """
        if not self.is_enabled():
            return None
        
        if not summary or len(summary.strip()) < 10:
            return None
        
        try:
            # Get embedding for current summary
            embedding = await self._embed(summary)
            if embedding is None:
                return None
            
            # Find most similar cached entry
            best_result, best_similarity = await self._find_similar(embedding)
            
            if best_similarity >= self.threshold:
                logger.info(f"Semantic cache HIT (similarity: {best_similarity:.3f})")
                return best_result
            else:
                logger.debug(f"Semantic cache MISS (best similarity: {best_similarity:.3f})")
                return None
                
        except Exception as e:
            logger.error(f"Semantic cache get error: {e}")
            return None
    
    async def set(self, summary: str, result: Dict[str, Any]):
        """
        Store summary-result pair with embedding.
        
        Args:
            summary: Normalized telemetry summary string
            result: Agent result to cache
        """
        if not self.is_enabled():
            return
        
        if not summary or len(summary.strip()) < 10:
            return
        
        try:
            embedding = await self._embed(summary)
            if embedding is None:
                return
            
            cache_key = self._make_key(summary)
            cache_entry = {
                "embedding": embedding.tolist(),
                "result": result,
                "summary_hash": self._hash(summary),
            }
            
            # Store in Redis if available
            if self.redis:
                try:
                    await self.redis.set(
                        cache_key,
                        json.dumps(cache_entry),
                        ttl=self.ttl
                    )
                    # Track the key so we can find it later
                    await self._add_cache_key(cache_key)
                    logger.debug(f"Cached result in Redis: {cache_key}")
                except Exception as e:
                    logger.warning(f"Redis cache write failed: {e}")
                    # Fallback to memory
                    self._memory_cache[cache_key] = (embedding, result)
            else:
                # Store in memory cache
                self._memory_cache[cache_key] = (embedding, result)
                
            logger.info(f"Semantic cache STORE (key: {cache_key[:20]}...)")
            
        except Exception as e:
            logger.error(f"Semantic cache set error: {e}")
    
    async def _embed(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for text using Gemini."""
        if not self.embeddings_model:
            return None
        
        try:
            # LangChain embeddings are synchronous, run in executor
            import asyncio
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: self.embeddings_model.embed_query(text)
            )
            return np.array(embedding)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None
    
    async def _find_similar(self, embedding: np.ndarray) -> Tuple[Optional[Dict], float]:
        """Find most similar cached entry."""
        best_result = None
        best_similarity = 0.0
        
        # Check Redis cache first
        if self.redis:
            try:
                # Scan for all semantic cache keys
                # Note: In production, use Redis SCAN with pattern
                keys = await self._get_cache_keys()
                
                for key in keys:
                    try:
                        data = await self.redis.get(key)
                        if data:
                            entry = json.loads(data)
                            cached_embedding = np.array(entry["embedding"])
                            similarity = self._cosine_similarity(embedding, cached_embedding)
                            
                            if similarity > best_similarity:
                                best_similarity = similarity
                                best_result = entry["result"]
                    except Exception:
                        continue
                        
            except Exception as e:
                logger.warning(f"Redis cache scan failed: {e}")
        
        # Also check memory cache
        for key, (cached_embedding, result) in self._memory_cache.items():
            similarity = self._cosine_similarity(embedding, cached_embedding)
            if similarity > best_similarity:
                best_similarity = similarity
                best_result = result
        
        return best_result, best_similarity
    
    async def _get_cache_keys(self) -> list:
        """Get all semantic cache keys from Redis."""
        if not self.redis:
            return []
        
        try:
            # Use Redis client's keys method (or scan for large datasets)
            # For now, we'll manage a key set
            keys_set_data = await self.redis.get("semantic_cache:keys")
            if keys_set_data:
                return json.loads(keys_set_data)
            return []
        except Exception:
            return []
    
    async def _add_cache_key(self, key: str):
        """Track cache key in Redis."""
        if not self.redis:
            return
        
        try:
            keys = await self._get_cache_keys()
            if key not in keys:
                keys.append(key)
                # Keep only last 100 keys to prevent unbounded growth
                if len(keys) > 100:
                    # Remove oldest keys
                    oldest_key = keys.pop(0)
                    await self.redis.delete(oldest_key)
                await self.redis.set("semantic_cache:keys", json.dumps(keys), ttl=self.ttl)
        except Exception:
            pass
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def _make_key(self, summary: str) -> str:
        """Generate Redis key for cache entry."""
        return f"semantic_cache:{self._hash(summary)}"
    
    def _hash(self, text: str) -> str:
        """Generate hash for text."""
        return hashlib.md5(text.encode()).hexdigest()


def generate_telemetry_summary(
    session_id: str,
    motor_state: str,
    motor_data: list,
    interaction_events: list,
    device_type: str = "desktop"
) -> str:
    """
    Generate a normalized summary string from telemetry data.
    This summary is used for embedding and similarity matching.
    
    Args:
        session_id: Session identifier
        motor_state: Classified motor state (jittery, determined, etc.)
        motor_data: List of motor telemetry samples
        interaction_events: List of interaction events
        device_type: Device type (desktop/mobile)
        
    Returns:
        Normalized summary string for embedding
    """
    parts = []
    
    # Device context
    parts.append(f"device:{device_type}")
    
    # Motor state (most important for similarity)
    parts.append(f"motor_state:{motor_state}")
    
    # Aggregate motor metrics
    if motor_data:
        avg_velocity = 0
        avg_acceleration = 0
        for sample in motor_data[-10:]:  # Last 10 samples
            if isinstance(sample, dict):
                vel = sample.get("velocity", {})
                acc = sample.get("acceleration", {})
                avg_velocity += (abs(vel.get("x", 0)) + abs(vel.get("y", 0))) / 2
                avg_acceleration += (abs(acc.get("x", 0)) + abs(acc.get("y", 0))) / 2
        
        if motor_data:
            avg_velocity /= min(len(motor_data), 10)
            avg_acceleration /= min(len(motor_data), 10)
        
        # Bucket velocity and acceleration
        velocity_bucket = "low" if avg_velocity < 100 else ("medium" if avg_velocity < 500 else "high")
        accel_bucket = "low" if avg_acceleration < 50 else ("medium" if avg_acceleration < 200 else "high")
        
        parts.append(f"velocity:{velocity_bucket}")
        parts.append(f"acceleration:{accel_bucket}")
    
    # Interaction event summary
    if interaction_events:
        event_types = {}
        target_categories = {}
        
        for event in interaction_events[-20:]:  # Last 20 events
            if isinstance(event, dict):
                etype = event.get("type", "unknown")
                event_types[etype] = event_types.get(etype, 0) + 1
                
                target = event.get("target_id", "")
                if target:
                    # Extract category from target (e.g., "product_card_1" -> "product_card")
                    category = "_".join(target.split("_")[:-1]) if "_" in target else target
                    target_categories[category] = target_categories.get(category, 0) + 1
        
        # Top event types
        top_events = sorted(event_types.items(), key=lambda x: -x[1])[:3]
        for etype, count in top_events:
            parts.append(f"event:{etype}:{count}")
        
        # Top target categories
        top_categories = sorted(target_categories.items(), key=lambda x: -x[1])[:3]
        for cat, count in top_categories:
            parts.append(f"target:{cat}:{count}")
    
    return " ".join(parts)


# Singleton instance
semantic_cache = SemanticCache()
