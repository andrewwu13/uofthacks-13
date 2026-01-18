"""
Redis key schema for session state management.
All keys are namespaced by session_id with TTLs.
"""
from typing import NamedTuple


class TTL:
    """TTL constants in seconds"""
    SESSION = 30 * 60  # 30 minutes
    CANDIDATES = 5 * 60  # 5 minutes
    LAYOUT = 30 * 60  # 30 minutes
    RECENTLY_USED = 30 * 60  # 30 minutes


class RedisKeys:
    """
    Redis key patterns for the pipeline.
    All methods return fully-qualified key strings.
    """
    
    @staticmethod
    def state(session_id: str) -> str:
        """Latest reducer output JSON"""
        return f"session:{session_id}:state"
    
    @staticmethod
    def constraints(session_id: str) -> str:
        """Derived hard/soft constraints JSON"""
        return f"session:{session_id}:constraints"
    
    @staticmethod
    def exploration_budget(session_id: str) -> str:
        """Float 0.0-1.0 exploration budget"""
        return f"session:{session_id}:exploration_budget"
    
    @staticmethod
    def candidates(session_id: str) -> str:
        """Top-K component IDs from vector search (JSON list)"""
        return f"session:{session_id}:candidates"
    
    @staticmethod
    def selected(session_id: str) -> str:
        """Final selected component IDs (JSON list)"""
        return f"session:{session_id}:selected"
    
    @staticmethod
    def layout_hash(session_id: str) -> str:
        """Hash of current layout for change detection"""
        return f"session:{session_id}:layout_hash"
    
    @staticmethod
    def layout(session_id: str) -> str:
        """Cached layout schema JSON"""
        return f"session:{session_id}:layout"
    
    @staticmethod
    def recently_used(session_id: str) -> str:
        """Set of recently shown component IDs"""
        return f"session:{session_id}:recently_used"
    
    @staticmethod
    def motor_state(session_id: str) -> str:
        """Current motor state (velocity, acceleration, cognitive state)"""
        return f"session:{session_id}:motor_state"


# Key metadata for documentation
KEY_SCHEMA = {
    "session:{id}:state": {"ttl": TTL.SESSION, "type": "json", "purpose": "Latest reducer output"},
    "session:{id}:constraints": {"ttl": TTL.SESSION, "type": "json", "purpose": "Hard/soft constraints"},
    "session:{id}:exploration_budget": {"ttl": TTL.SESSION, "type": "float", "purpose": "0.0-1.0"},
    "session:{id}:candidates": {"ttl": TTL.CANDIDATES, "type": "json_list", "purpose": "Top-K component IDs"},
    "session:{id}:selected": {"ttl": TTL.CANDIDATES, "type": "json_list", "purpose": "Final component IDs"},
    "session:{id}:layout_hash": {"ttl": TTL.LAYOUT, "type": "string", "purpose": "SHA256 of layout"},
    "session:{id}:layout": {"ttl": TTL.LAYOUT, "type": "json", "purpose": "Cached layout schema"},
    "session:{id}:recently_used": {"ttl": TTL.RECENTLY_USED, "type": "set", "purpose": "Component ID set"},
}
