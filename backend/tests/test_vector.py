"""
Unit tests for the Vector Module

Tests feature schema, module vectors, and vector store.
"""

import pytest
import math
from app.vector.feature_schema import FEATURE_DIMENSIONS, normalize_vector
from app.vector.module_vectors import get_module_by_id, MODULE_CATALOG
from app.vector.vector_store import VectorStore

class TestFeatureSchema:
    """Tests for feature_schema.py"""

    def test_feature_dimensions(self):
        """Verify feature dimension count for text-embedding-3-small"""
        assert FEATURE_DIMENSIONS == 1536

    def test_normalize_vector(self):
        """Normalized vector should have unit length"""
        vec = [0.1] * FEATURE_DIMENSIONS
        normalized = normalize_vector(vec)

        # Calculate magnitude
        magnitude = math.sqrt(sum(x**2 for x in normalized))
        assert abs(magnitude - 1.0) < 0.0001

    def test_normalize_zero_vector(self):
        """Normalizing zero vector should not crash"""
        vec = [0.0] * FEATURE_DIMENSIONS
        normalized = normalize_vector(vec)
        assert len(normalized) == FEATURE_DIMENSIONS


class TestModuleVectors:
    """Tests for module_vectors.py"""

    def test_module_catalog_not_empty(self):
        """Module catalog should have 36 entries"""
        assert len(MODULE_CATALOG) == 36

    def test_get_module_by_id(self):
        """Should find module by ID"""
        # ID 0 = genre:base, layout:standard
        module = get_module_by_id(0)
        assert module is not None
        assert module.layout == "standard"
        assert module.genre == "base"


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

    def test_cosine_similarity_identical(self):
        """Identical vectors should have similarity ~1.0"""
        store = VectorStore()

        vec = [0.1] * FEATURE_DIMENSIONS
        store.add("test", vec)

        results = store.search(vec, top_k=1)

        assert len(results) == 1
        assert results[0].score > 0.99 
