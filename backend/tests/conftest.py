"""
Pytest fixtures and configuration for backend unit tests.
Provides mocked database clients, Redis, and LLM services.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List
import numpy as np


# =========================================
# Async Event Loop Fixture
# =========================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# =========================================
# Mock Redis Client
# =========================================

class MockRedisClient:
    """Mock Redis client for testing without a real Redis connection."""
    
    def __init__(self):
        self._data: Dict[str, str] = {}
        self._locks: Dict[str, bool] = {}
    
    async def get(self, key: str) -> str | None:
        return self._data.get(key)
    
    async def set(self, key: str, value: str, ttl: int = None, ex: int = None, nx: bool = False) -> bool:
        if nx and key in self._data:
            return False
        self._data[key] = value
        return True
    
    async def delete(self, key: str) -> int:
        if key in self._data:
            del self._data[key]
            return 1
        return 0
    
    async def publish(self, channel: str, message: str):
        pass
    
    async def connect(self):
        pass
    
    async def disconnect(self):
        pass
    
    async def health_check(self) -> dict:
        return {"status": "connected", "latency_ms": 0.1}
    
    def clear(self):
        self._data.clear()
        self._locks.clear()


@pytest.fixture
def mock_redis():
    """Provide a mock Redis client instance."""
    return MockRedisClient()


# =========================================
# Mock MongoDB Client
# =========================================

class MockCollection:
    """Mock MongoDB collection."""
    
    def __init__(self):
        self._documents: List[Dict] = []
    
    async def insert_one(self, doc: Dict):
        self._documents.append(doc)
        return MagicMock(inserted_id="mock_id")
    
    async def insert_many(self, docs: List[Dict]):
        self._documents.extend(docs)
        return MagicMock(inserted_ids=["mock_id"] * len(docs))
    
    async def find_one(self, query: Dict) -> Dict | None:
        for doc in self._documents:
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None
    
    async def find(self, query: Dict = None):
        """Return an async iterator over matching documents."""
        class MockCursor:
            def __init__(self, docs):
                self._docs = docs
            
            def to_list(self, length=None):
                return asyncio.coroutine(lambda: self._docs)()
        
        return MockCursor(self._documents)
    
    async def create_index(self, *args, **kwargs):
        pass


class MockMongoClient:
    """Mock MongoDB client for testing."""
    
    def __init__(self):
        self.db = MagicMock()
        self._connected = False
        self._collections: Dict[str, MockCollection] = {}
    
    async def connect(self, max_retries=3, retry_delay=1.0):
        self._connected = True
    
    async def disconnect(self):
        self._connected = False
    
    async def health_check(self) -> dict:
        return {"status": "connected", "latency_ms": 0.5}
    
    @property
    def is_connected(self) -> bool:
        return self._connected
    
    def _get_collection(self, name: str) -> MockCollection:
        if name not in self._collections:
            self._collections[name] = MockCollection()
        return self._collections[name]
    
    @property
    def sessions(self):
        return self._get_collection("sessions")
    
    @property
    def preferences(self):
        return self._get_collection("preferences")
    
    @property
    def layouts(self):
        return self._get_collection("layouts")
    
    @property
    def telemetry(self):
        return self._get_collection("telemetry")


@pytest.fixture
def mock_mongo():
    """Provide a mock MongoDB client instance."""
    return MockMongoClient()


# =========================================
# Mock Embedding Model
# =========================================

class MockEmbeddingModel:
    """Mock embedding model that returns deterministic vectors."""
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self._cache: Dict[str, List[float]] = {}
    
    def embed_query(self, text: str) -> List[float]:
        """Generate a deterministic embedding based on text hash."""
        # Use hash for deterministic results
        seed = hash(text) % (2**32)
        np.random.seed(seed)
        embedding = np.random.rand(self.dimension).tolist()
        return embedding
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(t) for t in texts]


@pytest.fixture
def mock_embeddings():
    """Provide mock embeddings model."""
    return MockEmbeddingModel()


# =========================================
# Mock LLM for Agent Testing
# =========================================

class MockLLM:
    """Mock LLM that returns predefined responses for agent testing."""
    
    def __init__(self):
        self.call_count = 0
        self.responses: Dict[str, str] = {}
    
    async def ainvoke(self, prompt: str, **kwargs) -> str:
        self.call_count += 1
        # Return a structured response based on prompt content
        if "context" in prompt.lower():
            return '{"analysis": "user browsing products", "confidence": 0.8}'
        elif "variance" in prompt.lower():
            return '{"positive_variance": true, "engagement_delta": 0.15}'
        elif "stability" in prompt.lower():
            return '{"genre": "minimalist", "layout_type": "product-grid"}'
        elif "exploratory" in prompt.lower():
            return '{"genre": "loud", "layout_type": "hero", "exploration_score": 0.7}'
        else:
            return '{"result": "mock response"}'
    
    def invoke(self, prompt: str, **kwargs) -> str:
        self.call_count += 1
        return '{"result": "sync mock response"}'


@pytest.fixture
def mock_llm():
    """Provide mock LLM for testing."""
    return MockLLM()


# =========================================
# Sample Telemetry Data
# =========================================

@pytest.fixture
def sample_telemetry_batch():
    """Provide sample telemetry batch for testing."""
    return {
        "session_id": "test_session_123",
        "device_type": "desktop",
        "timestamp": 1737138008,
        "events": [
            {
                "ts": 1737138006,
                "type": "hover",
                "target_id": "product_card_1",
                "duration_ms": 450,
                "position": {"x": 500, "y": 300},
                "metadata": {"track_context": "price"}
            },
            {
                "ts": 1737138007,
                "type": "click",
                "target_id": "add_to_cart_btn",
                "position": {"x": 520, "y": 320},
                "metadata": {}
            }
        ],
        "motor": {
            "session_id": "test_session_123",
            "device": "mouse",
            "t0": 1737138005,
            "dt": 16,
            "samples": [
                [100, 200], [105, 202], [110, 205],
                [115, 208], [120, 210], [125, 213],
                [130, 216], [135, 218], [140, 220],
                [145, 222]
            ]
        }
    }


@pytest.fixture
def sample_motor_data():
    """Motor data with velocity and acceleration calculated."""
    return [
        {"timestamp": 100, "position": {"x": 100, "y": 200}, "velocity": {"x": 0, "y": 0}, "acceleration": {"x": 0, "y": 0}},
        {"timestamp": 116, "position": {"x": 105, "y": 202}, "velocity": {"x": 312.5, "y": 125}, "acceleration": {"x": 19531, "y": 7812}},
        {"timestamp": 132, "position": {"x": 110, "y": 205}, "velocity": {"x": 312.5, "y": 187.5}, "acceleration": {"x": 0, "y": 3906}},
    ]


@pytest.fixture
def sample_user_profile():
    """Sample user profile for vector testing."""
    return {
        "visual": {
            "color_scheme": "dark",
            "corner_radius": "rounded",
            "button_size": "medium",
            "density": "medium",
            "typography_weight": "regular"
        },
        "interaction": {
            "decision_confidence": "medium",
            "exploration_tolerance": "medium",
            "scroll_behavior": "moderate"
        },
        "behavioral": {
            "speed_vs_accuracy": "balanced",
            "engagement_depth": "moderate"
        },
        "inferred": {
            "summary": "User prefers clean dark interfaces",
            "visual_keywords": ["dark", "clean", "minimal"]
        }
    }


# =========================================
# Mock SSE Publisher
# =========================================

class MockSSEPublisher:
    """Mock SSE publisher for testing."""
    
    def __init__(self):
        self.published_messages: List[Dict] = []
    
    async def publish_layout_update(self, session_id: str, layout_update: Dict):
        self.published_messages.append({
            "session_id": session_id,
            "layout_update": layout_update
        })
    
    def subscribe(self, session_id: str):
        async def gen():
            yield {"data": "test"}
        return gen()


@pytest.fixture
def mock_sse_publisher():
    """Provide mock SSE publisher."""
    return MockSSEPublisher()


# =========================================
# Patch Decorators
# =========================================

@pytest.fixture
def patch_databases(mock_redis, mock_mongo):
    """Patch both Redis and MongoDB with mocks."""
    with patch('app.db.redis_client.redis_client', mock_redis), \
         patch('app.db.mongo_client.mongo_client', mock_mongo):
        yield mock_redis, mock_mongo
