"""
Unit tests for Semantic Cache

Tests cache operations with mocked embeddings - no API calls needed.
"""
import pytest
import asyncio
import json
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add cache directory to path - must be relative to backend/tests
cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../cache"))
if cache_dir not in sys.path:
    sys.path.insert(0, cache_dir)

from semantic_cache import SemanticCache, generate_telemetry_summary


class TestSemanticCacheUnit:
    """Unit tests for SemanticCache class without external dependencies."""
    
    def test_cache_initialization(self):
        """Cache should initialize with default values."""
        cache = SemanticCache()
        
        assert cache.threshold == 0.92
        assert cache.ttl == 3600
        assert cache.redis is None
        assert not cache.is_enabled()
    
    def test_cache_custom_threshold(self):
        """Cache should accept custom similarity threshold."""
        cache = SemanticCache(similarity_threshold=0.85)
        
        assert cache.threshold == 0.85
    
    def test_cosine_similarity_identical(self):
        """Identical vectors should have similarity 1.0."""
        cache = SemanticCache()
        
        vec = np.array([1.0, 0.0, 0.5, 0.3])
        similarity = cache._cosine_similarity(vec, vec)
        
        assert abs(similarity - 1.0) < 0.0001
    
    def test_cosine_similarity_orthogonal(self):
        """Orthogonal vectors should have similarity 0.0."""
        cache = SemanticCache()
        
        vec1 = np.array([1.0, 0.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0, 0.0])
        similarity = cache._cosine_similarity(vec1, vec2)
        
        assert abs(similarity) < 0.0001
    
    def test_cosine_similarity_opposite(self):
        """Opposite vectors should have similarity -1.0."""
        cache = SemanticCache()
        
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([-1.0, 0.0, 0.0])
        similarity = cache._cosine_similarity(vec1, vec2)
        
        assert abs(similarity + 1.0) < 0.0001
    
    def test_cosine_similarity_zero_vector(self):
        """Zero vectors should return 0.0 similarity."""
        cache = SemanticCache()
        
        vec1 = np.array([0.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])
        similarity = cache._cosine_similarity(vec1, vec2)
        
        assert similarity == 0.0
    
    def test_hash_deterministic(self):
        """Same text should produce same hash."""
        cache = SemanticCache()
        
        hash1 = cache._hash("test text")
        hash2 = cache._hash("test text")
        
        assert hash1 == hash2
    
    def test_hash_different_for_different_text(self):
        """Different text should produce different hashes."""
        cache = SemanticCache()
        
        hash1 = cache._hash("text one")
        hash2 = cache._hash("text two")
        
        assert hash1 != hash2
    
    def test_make_key_format(self):
        """Key should have semantic_cache: prefix."""
        cache = SemanticCache()
        
        key = cache._make_key("test summary")
        
        assert key.startswith("semantic_cache:")
        assert len(key) > len("semantic_cache:")


class TestSemanticCacheWithMockedEmbeddings:
    """Tests with mocked embedding model - no API calls."""
    
    @pytest.fixture
    def mock_cache(self, mock_embeddings, mock_redis):
        """Create cache with mocked embeddings and redis."""
        cache = SemanticCache()
        cache.embeddings_model = mock_embeddings
        cache._initialized = True
        cache.redis = mock_redis
        cache.threshold = 0.92
        return cache
    
    @pytest.mark.asyncio
    async def test_embed_returns_vector(self, mock_cache):
        """_embed should return numpy array."""
        embedding = await mock_cache._embed("test text")
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == 768  # Default dimension
    
    @pytest.mark.asyncio
    async def test_embed_deterministic(self, mock_cache):
        """Same text should produce same embedding."""
        embedding1 = await mock_cache._embed("identical text")
        embedding2 = await mock_cache._embed("identical text")
        
        np.testing.assert_array_almost_equal(embedding1, embedding2)
    
    @pytest.mark.asyncio
    async def test_set_stores_in_memory(self, mock_cache):
        """set() should store in memory cache."""
        mock_cache.redis = None  # Force memory cache
        
        await mock_cache.set("test summary text for caching", {"test": "result"})
        
        assert len(mock_cache._memory_cache) > 0
    
    @pytest.mark.asyncio
    async def test_get_returns_none_when_empty(self, mock_cache):
        """get() should return None when cache is empty."""
        result = await mock_cache.get("new query that doesn't exist")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_hit_with_similar_query(self, mock_cache):
        """Should return cached result for similar query."""
        mock_cache.redis = None
        mock_cache.threshold = 0.5  # Lower threshold for testing
        
        # Store a result
        await mock_cache.set("browsing products on mobile device", {"suggested_id": 5})
        
        # Query with same text (should be identical embedding)
        result = await mock_cache.get("browsing products on mobile device")
        
        assert result is not None
        assert result["suggested_id"] == 5
    
    @pytest.mark.asyncio
    async def test_skip_short_summaries(self, mock_cache):
        """Should skip summaries shorter than 10 characters."""
        await mock_cache.set("short", {"id": 1})
        result = await mock_cache.get("short")
        
        assert result is None


class TestTelemetrySummaryGeneration:
    """Tests for generate_telemetry_summary function."""
    
    def test_basic_summary_generation(self):
        """Should generate summary with basic fields."""
        summary = generate_telemetry_summary(
            session_id="test_123",
            motor_state="browsing",
            motor_data=[],
            interaction_events=[],
            device_type="desktop"
        )
        
        assert "device:desktop" in summary
        assert "motor_state:browsing" in summary
    
    def test_motor_state_included(self):
        """Motor state should be in summary."""
        for state in ["idle", "determined", "jittery", "browsing"]:
            summary = generate_telemetry_summary(
                session_id="test",
                motor_state=state,
                motor_data=[],
                interaction_events=[]
            )
            
            assert f"motor_state:{state}" in summary
    
    def test_velocity_bucketing(self):
        """Velocity should be bucketed into low/medium/high."""
        low_velocity_data = [
            {"velocity": {"x": 10, "y": 10}, "acceleration": {"x": 0, "y": 0}}
        ]
        
        summary = generate_telemetry_summary(
            session_id="test",
            motor_state="browsing",
            motor_data=low_velocity_data,
            interaction_events=[]
        )
        
        assert "velocity:low" in summary
    
    def test_interaction_events_counted(self):
        """Interaction events should be counted by type."""
        events = [
            {"type": "hover", "target_id": "product_1"},
            {"type": "hover", "target_id": "product_2"},
            {"type": "click", "target_id": "button_1"},
        ]
        
        summary = generate_telemetry_summary(
            session_id="test",
            motor_state="browsing",
            motor_data=[],
            interaction_events=events
        )
        
        assert "event:hover:2" in summary
        assert "event:click:1" in summary
    
    def test_target_categories_extracted(self):
        """Target categories should be extracted from target_id."""
        events = [
            {"type": "hover", "target_id": "product_card_1"},
            {"type": "hover", "target_id": "product_card_2"},
            {"type": "click", "target_id": "cta_button_1"},
        ]
        
        summary = generate_telemetry_summary(
            session_id="test",
            motor_state="idle",
            motor_data=[],
            interaction_events=events
        )
        
        assert "target:product_card:2" in summary or "target:" in summary


class TestSemanticCacheWithRedis:
    """Tests for Redis integration with mocked Redis client."""
    
    @pytest.mark.asyncio
    async def test_set_stores_in_redis(self, mock_redis, mock_embeddings):
        """set() should store in Redis when available."""
        cache = SemanticCache()
        cache.embeddings_model = mock_embeddings
        cache._initialized = True
        cache.redis = mock_redis
        
        await cache.set("test summary for redis storage test", {"id": 42})
        
        # Check Redis has the data
        assert len(mock_redis._data) > 0
    
    @pytest.mark.asyncio
    async def test_add_cache_key_tracks_keys(self, mock_redis, mock_embeddings):
        """_add_cache_key should track keys in Redis."""
        cache = SemanticCache()
        cache.embeddings_model = mock_embeddings
        cache._initialized = True
        cache.redis = mock_redis
        
        await cache._add_cache_key("semantic_cache:test_key")
        
        keys_data = await mock_redis.get("semantic_cache:keys")
        assert keys_data is not None
        keys = json.loads(keys_data)
        assert "semantic_cache:test_key" in keys
    
    @pytest.mark.asyncio
    async def test_get_cache_keys_returns_list(self, mock_redis, mock_embeddings):
        """_get_cache_keys should return list of keys."""
        cache = SemanticCache()
        cache.redis = mock_redis
        
        # Initially empty
        keys = await cache._get_cache_keys()
        assert keys == []
        
        # After adding
        await mock_redis.set("semantic_cache:keys", '["key1", "key2"]')
        keys = await cache._get_cache_keys()
        assert keys == ["key1", "key2"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
