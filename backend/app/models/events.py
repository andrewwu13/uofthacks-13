"""
Telemetry event models matching frontend payload
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any, Union


class MotorTelemetryPayload(BaseModel):
    session_id: str
    device: Literal["mouse", "touch"]
    t0: float
    dt: float
    samples: List[List[float]] = Field(..., description="List of [x, y] coordinates")


class TelemetryEvent(BaseModel):
    ts: float
    type: str # e.g., "click", "click_rage", "hover"
    target_id: str
    position: Optional[Dict[str, float]] = None # {x, y}
    duration_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class EventBatch(BaseModel):
    """
    Batch payload for POST /telemetry/events
    """
    session_id: str
    device_type: Literal["desktop", "mobile", "tablet"]
    timestamp: float
    events: List[TelemetryEvent]
    motor: Optional[MotorTelemetryPayload] = None


class EventResponse(BaseModel):
    received: int
    session_id: str
    status: str = "ok"
