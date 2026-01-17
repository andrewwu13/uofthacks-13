from pydantic import BaseModel
from typing import List, Literal, Union, Any, Optional

class LayoutMutation(BaseModel):
    op: Literal["add", "remove", "replace", "move"]
    slot: Optional[str] = None
    module: str

class LayoutUpdate(BaseModel):
    layout_id: str
    mutations: List[LayoutMutation]

