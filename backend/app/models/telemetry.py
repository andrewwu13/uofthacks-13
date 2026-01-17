from pydantic import BaseModel
from typing import List, Tuple, Literal, Optional

class MotorTelemetry(BaseModel):
    session_id: str
    device: Literal["mouse", "touch"]
    t0: int
    dt: int
    samples: List[List[int]]  # List of [x, y] coordinates

class TelemetryEvent(BaseModel):
    ts: int
    type: str # e.g., "hover", "enter_viewport"
    target_id: str
    duration_ms: Optional[int] = None

class TelemetryEventsBatch(BaseModel):
    session_id: str
    events: List[TelemetryEvent]
