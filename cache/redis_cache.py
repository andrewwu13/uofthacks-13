"""
Redis cache implementation
Primary real-time cache for session data
"""
import json
from typing import Any, Optional


class RedisCache:
    """
    Redis cache for real-time session data.
    Stores: motor state, session preference vector, last rendered layout hash.
    """
    
    def __init__(self, redis_client=None):
        self.client = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            return None
        value = await self.client.get(key)
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value with TTL in seconds"""
        if not self.client:
            return
        await self.client.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str):
        """Delete key"""
        if not self.client:
            return
        await self.client.delete(key)
    
    # Motor state cache
    async def get_motor_state(self, session_id: str) -> Optional[dict]:
        return await self.get(f"motor:{session_id}")
    
    async def set_motor_state(self, session_id: str, state: dict):
        await self.set(f"motor:{session_id}", state, ttl=60)
    
    # Preference vector cache
    async def get_preferences(self, session_id: str) -> Optional[dict]:
        return await self.get(f"prefs:{session_id}")
    
    async def set_preferences(self, session_id: str, prefs: dict):
        await self.set(f"prefs:{session_id}", prefs, ttl=3600)
    
    # Layout hash cache
    async def get_layout_hash(self, session_id: str) -> Optional[str]:
        return await self.get(f"layout_hash:{session_id}")
    
    async def set_layout_hash(self, session_id: str, hash_val: str):
        await self.set(f"layout_hash:{session_id}", hash_val, ttl=300)


redis_cache = RedisCache()
