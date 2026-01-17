"""
Redis client for real-time session data
"""
import redis.asyncio as redis
from app.config import settings


class RedisClient:
    """Async Redis client wrapper"""
    
    def __init__(self):
        self.client = None
    
    async def connect(self):
        """Connect to Redis"""
        self.client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
    
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
