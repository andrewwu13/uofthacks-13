"""
Caching service abstraction
"""
from typing import Optional, Any
import json


class CacheService:
    """Abstraction layer for caching operations"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None
        value = await self.redis.get(key)
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL"""
        if not self.redis:
            return
        await self.redis.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.redis:
            return
        await self.redis.delete(key)
    
    # Session-specific cache methods
    async def get_motor_state(self, session_id: str) -> Optional[dict]:
        """Get current motor state for session"""
        return await self.get(f"motor_state:{session_id}")
    
    async def set_motor_state(self, session_id: str, state: dict):
        """Set motor state for session"""
        await self.set(f"motor_state:{session_id}", state, ttl=60)
    
    async def get_preference_vector(self, session_id: str) -> Optional[dict]:
        """Get preference vector for session"""
        return await self.get(f"preferences:{session_id}")
    
    async def set_preference_vector(self, session_id: str, preferences: dict):
        """Set preference vector for session"""
        await self.set(f"preferences:{session_id}", preferences, ttl=3600)
    
    async def get_layout_hash(self, session_id: str) -> Optional[str]:
        """Get last rendered layout hash"""
        return await self.get(f"layout_hash:{session_id}")
    
    async def set_layout_hash(self, session_id: str, layout_hash: str):
        """Set layout hash"""
        await self.set(f"layout_hash:{session_id}", layout_hash, ttl=300)


cache_service = CacheService()
