"""
Redis client for real-time session data
"""
import redis.asyncio as redis
from app.config import settings
import logging
import time

logger = logging.getLogger(__name__)


class RedisClient:
    """Async Redis client wrapper with health check"""
    
    def __init__(self):
        self.client = None
        self._connected = False
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            # Verify connection
            await self.client.ping()
            self._connected = True
            logger.info(f"Connected to Redis: {settings.REDIS_URL}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            self._connected = False
            logger.info("Disconnected from Redis")
    
    async def health_check(self) -> dict:
        """Check Redis connection health"""
        if not self.client or not self._connected:
            return {"status": "disconnected", "error": "Client not initialized"}
        
        try:
            start = time.monotonic()
            await self.client.ping()
            latency_ms = (time.monotonic() - start) * 1000
            
            return {
                "status": "connected",
                "latency_ms": round(latency_ms, 2),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def get(self, key: str) -> str | None:
        """Get value by key"""
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, ttl: int = None, ex: int = None, nx: bool = False):
        """
        Set value with optional TTL and atomic lock support.
        
        Args:
            key: Redis key
            value: Value to set
            ttl: Time-to-live in seconds (legacy param, use `ex` instead)
            ex: Expiry time in seconds (standard redis param)
            nx: Only set if key does not exist (for distributed locking)
            
        Returns:
            bool: True if set succeeded, False if nx=True and key already exists
        """
        expiry = ex or ttl  # Prefer ex, fallback to ttl
        
        if nx:
            # Use SET with NX for atomic lock acquisition
            result = await self.client.set(key, value, ex=expiry, nx=True)
            return result is not None  # Returns None if key exists
        elif expiry:
            await self.client.setex(key, expiry, value)
            return True
        else:
            await self.client.set(key, value)
            return True
    
    async def delete(self, key: str):
        """Delete key"""
        await self.client.delete(key)
    
    async def publish(self, channel: str, message: str):
        """Publish message to channel"""
        await self.client.publish(channel, message)


redis_client = RedisClient()

