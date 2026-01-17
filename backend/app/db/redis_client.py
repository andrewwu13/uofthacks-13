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
    
    async def set(self, key: str, value: str, ttl: int = None):
        """Set value with optional TTL"""
        if ttl:
            await self.client.setex(key, ttl, value)
        else:
            await self.client.set(key, value)
    
    async def delete(self, key: str):
        """Delete key"""
        await self.client.delete(key)
    
    async def publish(self, channel: str, message: str):
        """Publish message to channel"""
        await self.client.publish(channel, message)


redis_client = RedisClient()

