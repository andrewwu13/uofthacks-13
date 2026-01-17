"""
Amplitude Analytics client
"""
from amplitude import Amplitude, BaseEvent
from typing import Optional, Dict, Any


class AmplitudeClient:
    """
    Client for Amplitude analytics.
    Tracks user behavior, layout changes, and conversion events.
    """
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.amplitude = Amplitude(api_key) if api_key else None
    
    def track(
        self,
        user_id: str,
        event_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Track an event"""
        if not self.amplitude:
            return
        
        event = BaseEvent(
            event_type=event_type,
            user_id=user_id,
            event_properties=properties or {},
        )
        self.amplitude.track(event)
    
    def track_layout_change(
        self,
        user_id: str,
        old_layout_hash: str,
        new_layout_hash: str,
        genres_used: list[str],
    ):
        """Track layout change event"""
        self.track(
            user_id=user_id,
            event_type="layout_changed",
            properties={
                "old_hash": old_layout_hash,
                "new_hash": new_layout_hash,
                "genres": genres_used,
            },
        )
    
    def track_loud_module_view(
        self,
        user_id: str,
        module_id: str,
        genre: str,
        dwell_time_ms: int,
    ):
        """Track loud module view for A/B testing"""
        self.track(
            user_id=user_id,
            event_type="loud_module_view",
            properties={
                "module_id": module_id,
                "genre": genre,
                "dwell_time_ms": dwell_time_ms,
            },
        )
    
    def track_conversion(
        self,
        user_id: str,
        product_id: str,
        revenue: float,
        layout_hash: str,
    ):
        """Track conversion event"""
        self.track(
            user_id=user_id,
            event_type="conversion",
            properties={
                "product_id": product_id,
                "revenue": revenue,
                "layout_hash": layout_hash,
            },
        )
    
    def flush(self):
        """Flush pending events"""
        if self.amplitude:
            self.amplitude.flush()


amplitude_client = AmplitudeClient()
