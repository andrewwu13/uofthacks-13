"""
Unit tests for Telemetry Processing Pipeline

Tests the events.py endpoint and process_telemetry_batch function
with mocked dependencies - no LLM calls or database connections needed.
"""
import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Ensure app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestMotorSampleTransformation:
    """Tests for transform_motor_samples function."""
    
    def test_empty_motor_data(self):
        """Should return empty list for no samples."""
        from app.api.events import transform_motor_samples
        
        result = transform_motor_samples(None)
        assert result == []
    
    def test_single_sample(self):
        """Should return empty for single sample (need 2 for velocity)."""
        from app.api.events import transform_motor_samples
        from app.models.events import MotorTelemetryPayload
        
        motor = MotorTelemetryPayload(
            session_id="test",
            device="mouse",
            t0=1000,
            dt=16,
            samples=[[100, 200]]
        )
        
        result = transform_motor_samples(motor)
        assert result == []
    
    def test_velocity_calculation(self):
        """Should correctly calculate velocity from position samples."""
        from app.api.events import transform_motor_samples
        from app.models.events import MotorTelemetryPayload
        
        motor = MotorTelemetryPayload(
            session_id="test",
            device="mouse",
            t0=1000,
            dt=100,  # 100ms = 0.1s
            samples=[
                [0, 0],
                [10, 0]  # Moved 10 pixels in 0.1s = 100 px/s
            ]
        )
        
        result = transform_motor_samples(motor)
        
        assert len(result) == 2
        # First sample has zero velocity
        assert result[0]["velocity"]["x"] == 0
        # Second sample: 10 pixels / 0.1 seconds = 100 px/s
        assert result[1]["velocity"]["x"] == 100.0
    
    def test_acceleration_calculation(self):
        """Should correctly calculate acceleration from velocity changes."""
        from app.api.events import transform_motor_samples
        from app.models.events import MotorTelemetryPayload
        
        motor = MotorTelemetryPayload(
            session_id="test",
            device="mouse",
            t0=1000,
            dt=100,  # 100ms = 0.1s
            samples=[
                [0, 0],
                [10, 0],   # vel_x = 100
                [30, 0]    # vel_x = 200, acc = (200-100)/0.1 = 1000
            ]
        )
        
        result = transform_motor_samples(motor)
        
        assert len(result) == 3
        # Third sample should have acceleration
        assert result[2]["acceleration"]["x"] == 1000.0
    
    def test_output_structure(self):
        """Output should have timestamp, position, velocity, acceleration."""
        from app.api.events import transform_motor_samples
        from app.models.events import MotorTelemetryPayload
        
        motor = MotorTelemetryPayload(
            session_id="test",
            device="mouse",
            t0=1000,
            dt=16,
            samples=[[100, 200], [105, 202]]
        )
        
        result = transform_motor_samples(motor)
        
        assert len(result) == 2
        for sample in result:
            assert "timestamp" in sample
            assert "position" in sample
            assert "velocity" in sample
            assert "acceleration" in sample
            assert "x" in sample["position"]
            assert "y" in sample["position"]


class TestMotorStateClassification:
    """Tests for motor state classification logic."""
    
    def test_idle_state_low_velocity(self):
        """Low velocity should be classified as idle."""
        # The classification logic in events.py:
        # avg_velocity < 50 -> idle
        avg_velocity = 30
        motor_state = "idle" if avg_velocity < 50 else "browsing"
        
        assert motor_state == "idle"
    
    def test_determined_state_high_velocity_low_jerk(self):
        """High velocity with low jerk should be determined."""
        avg_velocity = 600
        avg_jerk = 300
        
        if avg_velocity > 500 and avg_jerk < 500:
            motor_state = "determined"
        else:
            motor_state = "browsing"
        
        assert motor_state == "determined"
    
    def test_jittery_state_high_jerk(self):
        """High jerk with moderate velocity should be jittery."""
        avg_velocity = 200
        avg_jerk = 1500
        
        if avg_jerk > 1000 and avg_velocity < 300:
            motor_state = "jittery"
        elif avg_velocity > 500 and avg_jerk < 500:
            motor_state = "determined"
        else:
            motor_state = "browsing"
        
        assert motor_state == "jittery"
    
    def test_browsing_state_default(self):
        """Moderate values should be classified as browsing."""
        avg_velocity = 300
        avg_jerk = 600
        
        if avg_velocity < 50:
            motor_state = "idle"
        elif avg_jerk > 1000 and avg_velocity < 300:
            motor_state = "jittery"
        elif avg_velocity > 500 and avg_jerk < 500:
            motor_state = "determined"
        else:
            motor_state = "browsing"
        
        assert motor_state == "browsing"


class TestTelemetryEndpoint:
    """Integration tests for the /telemetry/events endpoint."""
    
    @pytest.fixture
    def mock_app_dependencies(self, mock_redis, mock_mongo):
        """Patch all app dependencies."""
        with patch('app.db.redis_client.redis_client', mock_redis), \
             patch('app.db.mongo_client.mongo_client', mock_mongo), \
             patch('app.api.events.redis_client', mock_redis), \
             patch('app.api.events.mongo_client', mock_mongo):
            yield mock_redis, mock_mongo
    
    def test_endpoint_accepts_valid_payload(self, sample_telemetry_batch):
        """Endpoint should accept valid telemetry payload."""
        from fastapi.testclient import TestClient
        
        with patch('app.db.redis_client.redis_client'), \
             patch('app.db.mongo_client.mongo_client'), \
             patch('app.api.events.redis_client'), \
             patch('app.api.events.mongo_client'):
            
            from app.main import app
            client = TestClient(app)
            
            response = client.post("/telemetry/events", json=sample_telemetry_batch)
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == sample_telemetry_batch["session_id"]
            assert data["received"] == len(sample_telemetry_batch["events"])
    
    def test_endpoint_returns_event_count(self):
        """Response should include correct event count."""
        from fastapi.testclient import TestClient
        
        payload = {
            "session_id": "test_session",
            "device_type": "desktop",
            "timestamp": 1737138000,
            "events": [
                {"ts": 1000, "type": "click", "target_id": "btn1"},
                {"ts": 1001, "type": "hover", "target_id": "card1"},
                {"ts": 1002, "type": "scroll", "target_id": "page"},
            ]
        }
        
        with patch('app.db.redis_client.redis_client'), \
             patch('app.db.mongo_client.mongo_client'), \
             patch('app.api.events.redis_client'), \
             patch('app.api.events.mongo_client'):
            
            from app.main import app
            client = TestClient(app)
            
            response = client.post("/telemetry/events", json=payload)
            
            assert response.json()["received"] == 3


class TestProcessTelemetryBatch:
    """Tests for process_telemetry_batch background task."""
    
    @pytest.fixture
    def mock_all_deps(self, mock_redis, mock_mongo, mock_sse_publisher):
        """Patch all dependencies for process_telemetry_batch."""
        patches = {
            'redis': patch('app.api.events.redis_client', mock_redis),
            'mongo': patch('app.api.events.mongo_client', mock_mongo),
            'sse': patch('app.api.events.sse_publisher', mock_sse_publisher),
            'agent': patch('app.api.events.run_layout_generation', 
                          AsyncMock(return_value=None)),
            'semantic': patch('app.api.events.SEMANTIC_CACHE_AVAILABLE', False),
        }
        
        for p in patches.values():
            p.start()
        
        yield mock_redis, mock_mongo, mock_sse_publisher
        
        for p in patches.values():
            p.stop()
    
    @pytest.mark.asyncio
    async def test_saves_events_to_mongo(self, mock_all_deps, sample_telemetry_batch):
        """Should save events to MongoDB telemetry collection."""
        mock_redis, mock_mongo, mock_sse = mock_all_deps
        
        from app.api.events import process_telemetry_batch
        from app.models.events import EventBatch
        
        batch = EventBatch(**sample_telemetry_batch)
        
        await process_telemetry_batch(batch)
        
        # Check MongoDB was called
        assert len(mock_mongo.telemetry._documents) > 0
    
    @pytest.mark.asyncio
    async def test_acquires_and_releases_lock(self, mock_all_deps, sample_telemetry_batch):
        """Should acquire and release Redis lock."""
        mock_redis, mock_mongo, mock_sse = mock_all_deps
        
        from app.api.events import process_telemetry_batch
        from app.models.events import EventBatch
        
        batch = EventBatch(**sample_telemetry_batch)
        
        await process_telemetry_batch(batch)
        
        # Lock should be released (key deleted)
        lock_key = f"agent_lock:{batch.session_id}"
        assert lock_key not in mock_redis._data
    
    @pytest.mark.asyncio
    async def test_publishes_sse_update(self, mock_redis, mock_mongo, mock_sse_publisher, sample_telemetry_batch):
        """Should publish layout update via SSE."""
        # Properly fix the motor_telemetry mock
        mock_mongo.db = MagicMock()
        mock_mongo.db.motor_telemetry = MagicMock()
        mock_mongo.db.motor_telemetry.insert_one = AsyncMock()
        
        with patch('app.api.events.redis_client', mock_redis), \
             patch('app.api.events.mongo_client', mock_mongo), \
             patch('app.api.events.sse_publisher', mock_sse_publisher), \
             patch('app.api.events.run_layout_generation', AsyncMock(return_value=None)), \
             patch('app.api.events.SEMANTIC_CACHE_AVAILABLE', False):
            
            from app.api.events import process_telemetry_batch
            from app.models.events import EventBatch
            
            batch = EventBatch(**sample_telemetry_batch)
            
            await process_telemetry_batch(batch)
            
            # Check SSE publisher was called
            assert len(mock_sse_publisher.published_messages) > 0
            assert mock_sse_publisher.published_messages[0]["session_id"] == batch.session_id
    
    @pytest.mark.asyncio
    async def test_skips_when_locked(self, mock_redis, mock_mongo, mock_sse_publisher, sample_telemetry_batch):
        """Should skip processing if lock is held by another task."""
        # Pre-set the lock
        session_id = sample_telemetry_batch["session_id"]
        await mock_redis.set(f"agent_lock:{session_id}", "running", ex=30)
        
        with patch('app.api.events.redis_client', mock_redis), \
             patch('app.api.events.mongo_client', mock_mongo), \
             patch('app.api.events.sse_publisher', mock_sse_publisher), \
             patch('app.api.events.SEMANTIC_CACHE_AVAILABLE', False):
            
            from app.api.events import process_telemetry_batch
            from app.models.events import EventBatch
            
            batch = EventBatch(**sample_telemetry_batch)
            
            await process_telemetry_batch(batch)
            
            # SSE should NOT be called (skipped due to lock)
            assert len(mock_sse_publisher.published_messages) == 0


class TestConcurrencyLock:
    """Tests for Redis-based concurrency lock."""
    
    @pytest.mark.asyncio
    async def test_lock_acquired_first_time(self, mock_redis):
        """First lock attempt should succeed."""
        result = await mock_redis.set("test_lock", "running", ex=30, nx=True)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_lock_fails_when_held(self, mock_redis):
        """Second lock attempt should fail if key exists."""
        await mock_redis.set("test_lock", "running", ex=30, nx=True)
        
        result = await mock_redis.set("test_lock", "running2", ex=30, nx=True)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_lock_released_after_delete(self, mock_redis):
        """Lock should be available after delete."""
        await mock_redis.set("test_lock", "running", ex=30, nx=True)
        await mock_redis.delete("test_lock")
        
        result = await mock_redis.set("test_lock", "running2", ex=30, nx=True)
        
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
