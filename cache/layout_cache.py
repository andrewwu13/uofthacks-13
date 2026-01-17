"""
Layout cache for pre-computed layout directives
Keys by page type + device type for quick frontend rehydration
"""
import hashlib
import json
from typing import Optional


class LayoutCache:
    """
    Cache for layout directives in JSON format.
    Keyed by: session_id + page_type + device_type
    Allows frontend to rehydrate components quickly.
    """
    
    def __init__(self, redis_client=None):
        self.client = redis_client
        self.default_ttl = 300  # 5 minutes
    
    def _make_key(self, session_id: str, page_type: str, device_type: str) -> str:
        """Generate cache key"""
        return f"layout:{session_id}:{page_type}:{device_type}"
    
    async def get(
        self,
        session_id: str,
        page_type: str,
        device_type: str,
    ) -> Optional[dict]:
        """Get cached layout"""
        if not self.client:
            return None
        
        key = self._make_key(session_id, page_type, device_type)
        value = await self.client.get(key)
        return json.loads(value) if value else None
    
    async def set(
        self,
        session_id: str,
        page_type: str,
        device_type: str,
        layout: dict,
        ttl: Optional[int] = None,
    ):
        """Cache layout directive"""
        if not self.client:
            return
        
        key = self._make_key(session_id, page_type, device_type)
        await self.client.setex(
            key,
            ttl or self.default_ttl,
            json.dumps(layout),
        )
    
    async def invalidate(
        self,
        session_id: str,
        page_type: Optional[str] = None,
        device_type: Optional[str] = None,
    ):
        """Invalidate cached layouts"""
        if not self.client:
            return
        
        if page_type and device_type:
            key = self._make_key(session_id, page_type, device_type)
            await self.client.delete(key)
        else:
            # Invalidate all layouts for session
            pattern = f"layout:{session_id}:*"
            async for key in self.client.scan_iter(pattern):
                await self.client.delete(key)
    
    def compute_hash(self, layout: dict) -> str:
        """Compute hash of layout for change detection"""
        return hashlib.md5(json.dumps(layout, sort_keys=True).encode()).hexdigest()


layout_cache = LayoutCache()
