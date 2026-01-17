"""
Session models
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any


class SessionCreate(BaseModel):
    device_type: Optional[str] = "desktop"


class SessionResponse(BaseModel):
    session_id: str
    preferences: Optional[Dict[str, Any]] = None


class SessionPreferences(BaseModel):
    preferred_genre: Optional[str] = None
    color_preference: Optional[Dict[str, str]] = None
    typography_preference: Optional[Dict[str, Any]] = None
    interaction_style: Optional[str] = None  # "minimalist", "detailed", etc.
