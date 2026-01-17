"""
Layout schema models
"""
from pydantic import BaseModel
from typing import List, Optional


class DesignTokenOverrides(BaseModel):
    primary_color: Optional[str] = None
    accent_color: Optional[str] = None
    font_family: Optional[str] = None
    font_weight: Optional[int] = None
    border_radius: Optional[int] = None
    spacing: Optional[int] = None


class LayoutModule(BaseModel):
    id: str
    type: str
    genre: str
    props: dict
    is_loud: bool = False


class LayoutSection(BaseModel):
    id: str
    modules: List[LayoutModule]


class LayoutSchema(BaseModel):
    version: str
    session_id: str
    timestamp: int
    sections: List[LayoutSection]
    design_tokens: Optional[DesignTokenOverrides] = None


class LayoutRequest(BaseModel):
    session_id: str
    page: str = "home"
    force_refresh: bool = False
