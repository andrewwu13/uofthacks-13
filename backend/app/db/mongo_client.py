"""
MongoDB client for cold storage
Production-ready with connection pooling, retries, and health checks
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)


class MongoClient:
    """
    Async MongoDB client wrapper with production features:
    - Connection pooling
    - Retry logic with exponential backoff
    - Health check method
    - Index management
    """
    
    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None
        self._connected: bool = False
    
    async def connect(self, max_retries: int = 3, retry_delay: float = 1.0) -> None:
        """
        Connect to MongoDB with retry logic.
        
        Args:
            max_retries: Maximum number of connection attempts
            retry_delay: Initial delay between retries (doubles each attempt)
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Connecting to MongoDB (attempt {attempt + 1}/{max_retries})...")
                
                self.client = AsyncIOMotorClient(
                    settings.MONGODB_URL,
                    minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                    maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                    serverSelectionTimeoutMS=settings.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
                    connectTimeoutMS=settings.MONGODB_CONNECT_TIMEOUT_MS,
                )
                
                # Verify connection by pinging the server
                await self.client.admin.command('ping')
                
                self.db = self.client[settings.MONGODB_DATABASE]
                self._connected = True
                
                logger.info(f"Connected to MongoDB: {settings.MONGODB_DATABASE}")
                
                # Create indexes on startup
                await self._ensure_indexes()
                
                return
                
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.warning(f"MongoDB connection attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (2 ** attempt))
                else:
                    logger.error("Failed to connect to MongoDB after all retries")
                    raise
    
    async def disconnect(self) -> None:
        """Disconnect from MongoDB gracefully"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("Disconnected from MongoDB")
    
    async def health_check(self) -> dict:
        """
        Check MongoDB connection health.
        
        Returns:
            dict with status and latency information
        """
        if not self.client or not self._connected:
            return {"status": "disconnected", "error": "Client not initialized"}
        
        try:
            import time
            start = time.monotonic()
            await self.client.admin.command('ping')
            latency_ms = (time.monotonic() - start) * 1000
            
            return {
                "status": "connected",
                "database": settings.MONGODB_DATABASE,
                "latency_ms": round(latency_ms, 2),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _ensure_indexes(self) -> None:
        """
        Create indexes for optimal query performance.
        Indexes are created in the background and are idempotent.
        """
        try:
            # Telemetry collection indexes
            # Compound index for session-based time queries
            await self.telemetry.create_index(
                [("session_id", 1), ("timestamp", -1)],
                background=True,
                name="session_timestamp_idx"
            )
            
            # TTL index to auto-expire old telemetry after 30 days
            await self.telemetry.create_index(
                "timestamp",
                expireAfterSeconds=30 * 24 * 60 * 60,  # 30 days
                background=True,
                name="telemetry_ttl_idx"
            )
            
            # Sessions collection
            await self.sessions.create_index(
                "session_id",
                unique=True,
                background=True,
                name="session_id_unique_idx"
            )
            await self.sessions.create_index(
                "created_at",
                expireAfterSeconds=7 * 24 * 60 * 60,  # 7 days TTL
                background=True,
                name="sessions_ttl_idx"
            )
            
            # Preferences collection
            await self.preferences.create_index(
                "session_id",
                unique=True,
                background=True,
                name="preferences_session_idx"
            )
            
            # Layouts collection
            await self.layouts.create_index(
                [("session_id", 1), ("page", 1)],
                background=True,
                name="layouts_session_page_idx"
            )
            
            logger.info("MongoDB indexes ensured")
            
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._connected
    
    # =========================================
    # Collection Accessors
    # =========================================
    
    @property
    def sessions(self):
        """Sessions collection - active user sessions"""
        return self.db.sessions
    
    @property
    def preferences(self):
        """User preferences collection - learned style preferences"""
        return self.db.preferences
    
    @property
    def layouts(self):
        """Generated layouts collection - cached layout schemas"""
        return self.db.layouts
    
    @property
    def telemetry(self):
        """Raw telemetry data collection - motor + interaction events"""
        return self.db.telemetry
    
    @property
    def analytics(self):
        """Aggregated analytics collection"""
        return self.db.analytics


# Singleton instance
mongo_client = MongoClient()
