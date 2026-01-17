"""
Telemetry event models
"""
from pydantic import BaseModel
from typing import List, Optional, Literal


class MouseTelemetry(BaseModel):
    timestamp: float
    x: float
    y: float
    velocity: dict  # {x: float, y: float}
    acceleration: dict  # {x: float, y: float}


class TouchTelemetry(BaseModel):
    timestamp: float
    touches: List[dict]  # [{x, y, identifier}]
    scroll_velocity: float
    scroll_acceleration: float


class ScrollTelemetry(BaseModel):
    timestamp: float
    scroll_y: float
    scroll_percent: float
    direction: Literal["up", "down", "none"]
    velocity: float
    dwell_time: float


class InteractionEvent(BaseModel):
    timestamp: float
    type: Literal["click", "hover-enter", "hover-leave", "focus", "blur"]
    target: dict  # {moduleId, moduleType, moduleGenre, isLoud, tagName, textContent}
    duration: Optional[float] = None
    position: dict  # {x, y}


class TelemetryEvent(BaseModel):
    type: Literal["mouse", "touch", "scroll", "interaction"]
    data: dict


class EventBatch(BaseModel):
    session_id: str
    device_type: Literal["desktop", "mobile", "tablet"]
    timestamp: int
    events: List[TelemetryEvent]


class EventResponse(BaseModel):
    received: int
    session_id: str


class ProductModel(BaseModel):
    id: str
    title: str
    price: float
    image_url: str
    description: Optional[str] = None
    category: Optional[str] = None
