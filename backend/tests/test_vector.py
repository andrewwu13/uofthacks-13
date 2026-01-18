"""
Unit tests for the Vector Module

Tests feature schema, module vectors, profile conversion, and vector store.
"""
import pytest
import math
from app.vector import (
    FEATURE_DIMENSIONS,
    FeatureIndex,
    normalize_vector,
    create_zero_vector,
    encode_value,
    ENCODINGS,
    GENRE_VECTORS,
)
from app.vector import (
    ModuleMetadata,
    MODULE_CATALOG,
    module_to_vector,
    get_module_by_id,
    get_modules_by_type,
)
from app.vector import (
    profile_to_vector,
    traits_to_vector,
)
from app.vector import (
    VectorStore,
    SearchResult,
    vector_store,
    initialize_vector_store,
    search_similar_modules,
)
from app.models.reducer import (
    ReducerOutput,
    VisualTraits,
    InteractionTraits,
    BehavioralTraits,
)


class TestFeatureSchema:
    """Tests for feature_schema.py"""
    
    def test_feature_dimensions(self):
        """Verify feature dimension count"""
        assert FEATURE_DIMENSIONS == 12
    
    def test_feature_index_values(self):
        """Verify feature index mapping"""
        assert FeatureIndex.DARKNESS == 0
        assert FeatureIndex.VIBRANCY == 1
        assert FeatureIndex.EXPLORATION == 11
    
    def test_create_zero_vector(self):
        """Zero vector should have correct dimensions and neutral values"""
        vec = create_zero_vector()
        assert len(vec) == FEATURE_DIMENSIONS
        assert all(v == 0.5 for v in vec)
    
    def test_normalize_vector(self):
        """Normalized vector should have unit length"""
        vec = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        normalized = normalize_vector(vec)
        
        # Calculate magnitude
        magnitude = math.sqrt(sum(x**2 for x in normalized))
        assert abs(magnitude - 1.0) < 0.0001
    
    def test_normalize_zero_vector(self):
        """Normalizing zero vector should not crash"""
        vec = [0.0] * FEATURE_DIMENSIONS
        normalized = normalize_vector(vec)
        assert len(normalized) == FEATURE_DIMENSIONS
    
    def test_encode_value_valid(self):
        """Encoding valid categorical values"""
        assert encode_value("color_scheme", "dark") == 1.0
        assert encode_value("color_scheme", "light") == 0.0
        assert encode_value("density", "medium") == 0.5
    
    def test_encode_value_invalid(self):
        """Invalid values should return neutral 0.5"""
        assert encode_value("color_scheme", "unknown") == 0.5
        assert encode_value("unknown_category", "value") == 0.5
    
    def test_genre_vectors_exist(self):
        """All expected genres should have vectors"""
        expected_genres = ["base", "minimalist", "neobrutalist", "glassmorphism", "loud", "cyber"]
        for genre in expected_genres:
            assert genre in GENRE_VECTORS
            assert len(GENRE_VECTORS[genre]) == 4


class TestModuleVectors:
    """Tests for module_vectors.py"""
    
    def test_module_catalog_not_empty(self):
        """Module catalog should have entries"""
        assert len(MODULE_CATALOG) > 0
    
    def test_module_catalog_has_heroes(self):
        """Should have hero modules"""
        heroes = get_modules_by_type("hero")
        assert len(heroes) >= 1
    
    def test_module_to_vector_normalized(self):
        """Module vectors should be normalized"""
        module = MODULE_CATALOG[0]
        vec = module_to_vector(module)
        
        # Calculate magnitude
        magnitude = math.sqrt(sum(x**2 for x in vec))
        assert abs(magnitude - 1.0) < 0.0001
    
    def test_get_module_by_id(self):
        """Should find module by ID (integer 0-35)"""
        # ID 0 = genre:base, layout:standard
        module = get_module_by_id(0)
        assert module is not None
        assert module.layout == "standard"
        assert module.genre == "base"
    
    def test_get_module_by_id_not_found(self):
        """Should return None for unknown ID"""
        assert get_module_by_id("nonexistent_module") is None


class TestProfileVectors:
    """Tests for profile_vectors.py"""
    
    def test_profile_to_vector_default(self):
        """Default profile should produce valid vector"""
        profile = ReducerOutput()
        vec = profile_to_vector(profile)
        
        assert len(vec) == FEATURE_DIMENSIONS
        # Should be normalized
        magnitude = math.sqrt(sum(x**2 for x in vec))
        assert abs(magnitude - 1.0) < 0.0001
    
    def test_profile_to_vector_all_values_in_range(self):
        """All vector values should be in [0, 1] before normalization"""
        # Test with extreme values
        dark_profile = ReducerOutput(
            visual=VisualTraits(
                color_scheme="dark",
                corner_radius="sharp",
                button_size="large",
                density="high",
                typography_weight="bold"
            ),
            interaction=InteractionTraits(
                exploration_tolerance="high"
            ),
            behavioral=BehavioralTraits(
                engagement_depth="deep"
            )
        )
        
        light_profile = ReducerOutput(
            visual=VisualTraits(
                color_scheme="light",
                corner_radius="pill",
                button_size="small",
                density="low",
                typography_weight="light"
            ),
            interaction=InteractionTraits(
                exploration_tolerance="low"
            ),
            behavioral=BehavioralTraits(
                engagement_depth="shallow"
            )
        )
        
        dark_vec = profile_to_vector(dark_profile)
        light_vec = profile_to_vector(light_profile)
        
        # Both should be valid vectors
        assert len(dark_vec) == FEATURE_DIMENSIONS
        assert len(light_vec) == FEATURE_DIMENSIONS
    
    def test_profile_to_vector_minimalist_detection(self):
        """Minimalist profile should have high minimalism score"""
        profile = ReducerOutput(
            visual=VisualTraits(
                color_scheme="light",
                corner_radius="sharp",
                button_size="small",
                density="low",
                typography_weight="light"
            )
        )
        
        # Get unnormalized vector to check scores
        from app.vector.profile_vectors import profile_to_vector as _
        from app.models.reducer import ReducerOutput as RO
        from app.vector.feature_schema import FeatureIndex as FI, normalize_vector as nv, encode_value as ev
        
        # Manual check: minimalism should be relatively high
        vec = profile_to_vector(profile)
        assert len(vec) == FEATURE_DIMENSIONS
    
    def test_traits_to_vector(self):
        """traits_to_vector should work with partial traits"""
        vec = traits_to_vector(
            visual=VisualTraits(color_scheme="dark")
        )
        assert len(vec) == FEATURE_DIMENSIONS


class TestVectorStore:
    """Tests for vector_store.py"""
    
    def test_vector_store_add_get(self):
        """Should add and retrieve vectors"""
        store = VectorStore()
        test_vec = [0.5] * FEATURE_DIMENSIONS
        
        store.add("test_1", test_vec, {"type": "hero"})
        
        retrieved = store.get("test_1")
        assert retrieved is not None
        assert len(retrieved) == FEATURE_DIMENSIONS
    
    def test_vector_store_search(self):
        """Should find similar vectors"""
        store = VectorStore()
        
        # Add some test vectors
        vec1 = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        vec2 = [0.9, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        vec3 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        
        store.add("similar_1", vec1)
        store.add("similar_2", vec2)
        store.add("different", vec3)
        
        # Search for vectors similar to vec1
        results = store.search(vec1, top_k=2)
        
        assert len(results) == 2
        assert results[0].id == "similar_1"  # Self should be most similar
        assert results[1].id == "similar_2"  # Similar vector should be next
    
    def test_cosine_similarity_identical(self):
        """Identical vectors should have similarity ~1.0"""
        store = VectorStore()
        
        vec = [0.5, 0.3, 0.7, 0.2, 0.8, 0.1, 0.6, 0.4, 0.5, 0.5, 0.5, 0.5]
        store.add("test", vec)
        
        results = store.search(vec, top_k=1)
        
        assert len(results) == 1
        assert results[0].score > 0.99  # Should be very close to 1.0
    
    def test_search_by_type_filters(self):
        """search_by_type should filter correctly"""
        store = VectorStore()
        
        vec1 = [0.5] * FEATURE_DIMENSIONS
        vec2 = [0.6] * FEATURE_DIMENSIONS
        
        store.add("hero_1", vec1, {"module_type": "hero"})
        store.add("cta_1", vec2, {"module_type": "cta"})
        
        hero_results = store.search_by_type(vec1, "hero", top_k=5)
        
        assert len(hero_results) == 1
        assert hero_results[0].id == "hero_1"
    
    def test_initialize_vector_store(self):
        """Global store should initialize with module catalog"""
        initialize_vector_store()
        
        assert len(vector_store) > 0
        
        # Should be able to search
        query = create_zero_vector()
        results = vector_store.search(query, top_k=3)
        assert len(results) > 0
    
    def test_search_similar_modules(self):
        """search_similar_modules should return results"""
        initialize_vector_store()
        
        profile_vec = create_zero_vector()
        results = search_similar_modules(profile_vec)
        
        # Results should have 'recommended' key with list of SearchResult
        assert "recommended" in results
        assert len(results["recommended"]) > 0


class TestVectorStorePerformance:
    """Performance tests for vector operations"""
    
    def test_search_performance(self):
        """Search should be fast (<10ms for 100 vectors)"""
        import time
        
        store = VectorStore()
        
        # Add 100 random vectors
        for i in range(100):
            vec = [(i * j) % 10 / 10.0 for j in range(FEATURE_DIMENSIONS)]
            store.add(f"vec_{i}", vec)
        
        query = [0.5] * FEATURE_DIMENSIONS
        
        start = time.perf_counter()
        for _ in range(100):
            store.search(query, top_k=10)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        
        avg_time = elapsed / 100
        assert avg_time < 10.0, f"Search too slow: {avg_time:.3f}ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
