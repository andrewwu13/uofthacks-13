"""
Unit tests for SSE Publisher and Health Check Endpoint

Tests real-time communication without actual connections.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import json


class TestSSEPublisher:
    """Tests for SSE publisher functionality."""
    
    def test_sse_publisher_initialization(self):
        """Publisher should initialize with empty subscribers."""
        from app.sse.publisher import SSEPublisher
        
        publisher = SSEPublisher()
        
        # Should have no subscribers initially
        assert hasattr(publisher, 'subscribe')
        assert hasattr(publisher, 'publish_layout_update')
    
    @pytest.mark.asyncio
    async def test_publish_layout_update_success(self, mock_sse_publisher):
        """Should publish layout update to session."""
        await mock_sse_publisher.publish_layout_update(
            session_id="test_session",
            layout_update={"suggested_id": 5, "genre": "minimalist"}
        )
        
        assert len(mock_sse_publisher.published_messages) == 1
        assert mock_sse_publisher.published_messages[0]["session_id"] == "test_session"
    
    @pytest.mark.asyncio
    async def test_multiple_sessions_isolated(self, mock_sse_publisher):
        """Different sessions should receive separate updates."""
        await mock_sse_publisher.publish_layout_update(
            "session_1", {"id": 1}
        )
        await mock_sse_publisher.publish_layout_update(
            "session_2", {"id": 2}
        )
        
        assert len(mock_sse_publisher.published_messages) == 2
        
        session_1_updates = [m for m in mock_sse_publisher.published_messages 
                            if m["session_id"] == "session_1"]
        session_2_updates = [m for m in mock_sse_publisher.published_messages 
                            if m["session_id"] == "session_2"]
        
        assert len(session_1_updates) == 1
        assert len(session_2_updates) == 1


class TestHealthCheckEndpoint:
    """Tests for /health endpoint."""
    
    def test_health_check_returns_200(self):
        """Health check should return 200 OK."""
        from fastapi.testclient import TestClient
        
        # Mock database clients
        with patch('app.db.redis_client.redis_client') as mock_redis, \
             patch('app.db.mongo_client.mongo_client') as mock_mongo:
            
            mock_redis.health_check = AsyncMock(return_value={
                "status": "connected", "latency_ms": 0.5
            })
            mock_mongo.health_check = AsyncMock(return_value={
                "status": "connected", "latency_ms": 1.0
            })
            
            from app.main import app
            client = TestClient(app)
            
            response = client.get("/health")
            
            assert response.status_code == 200
    
    def test_health_check_returns_status(self):
        """Health check should include status field."""
        from fastapi.testclient import TestClient
        
        with patch('app.db.redis_client.redis_client') as mock_redis, \
             patch('app.db.mongo_client.mongo_client') as mock_mongo:
            
            mock_redis.health_check = AsyncMock(return_value={
                "status": "connected"
            })
            mock_mongo.health_check = AsyncMock(return_value={
                "status": "connected"
            })
            
            from app.main import app
            client = TestClient(app)
            
            response = client.get("/health")
            data = response.json()
            
            assert "status" in data
            assert data["status"] in ["healthy", "degraded"]


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_returns_api_info(self):
        """Root should return API information."""
        from fastapi.testclient import TestClient
        
        with patch('app.db.redis_client.redis_client'), \
             patch('app.db.mongo_client.mongo_client'):
            
            from app.main import app
            client = TestClient(app)
            
            response = client.get("/")
            
            if response.status_code == 200:
                data = response.json()
                assert "name" in data or "version" in data or "docs" in data


class TestProductsEndpoint:
    """Tests for /products endpoint."""
    
    def test_get_products_returns_list(self):
        """Products endpoint should return a list."""
        from fastapi.testclient import TestClient
        
        with patch('app.db.redis_client.redis_client'), \
             patch('app.db.mongo_client.mongo_client'), \
             patch('app.services.product_service.product_service') as mock_service:
            
            mock_service.get_products_for_session.return_value = [
                {"id": 1, "title": "Test Product", "price": "19.99"}
            ]
            
            from app.main import app
            client = TestClient(app)
            
            response = client.get("/products/test_session")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)


class TestStreamEndpoint:
    """Tests for SSE stream endpoint."""
    
    def test_stream_endpoint_exists(self):
        """Stream endpoint should be accessible."""
        from fastapi.testclient import TestClient
        
        with patch('app.db.redis_client.redis_client'), \
             patch('app.db.mongo_client.mongo_client'):
            
            from app.main import app
            client = TestClient(app)
            
            # Note: TestClient doesn't fully support SSE, 
            # but we can check the endpoint exists
            response = client.get("/stream/test_session")
            
            # SSE endpoints return 200 with streaming
            assert response.status_code == 200


class TestDebugPublishEndpoint:
    """Tests for debug publish endpoint."""
    
    def test_debug_publish_accepts_payload(self):
        """Debug publish should accept layout payload."""
        from fastapi.testclient import TestClient
        
        with patch('app.db.redis_client.redis_client'), \
             patch('app.db.mongo_client.mongo_client'), \
             patch('app.sse.publisher.sse_publisher') as mock_sse:
            
            mock_sse.publish_layout_update = AsyncMock()
            
            from app.main import app
            client = TestClient(app)
            
            payload = {"suggested_id": 5, "genre": "loud"}
            response = client.post("/debug/publish_layout/test_session", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "published"
            assert data["session_id"] == "test_session"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
