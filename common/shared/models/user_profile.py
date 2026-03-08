"""
Pydantic models for the User Profile JSON schema.
Used for vectorization and module matching.
"""

from pydantic import BaseModel
from typing import Literal, Optional


class UserProfile(BaseModel):
    """
    Condensed user profile for vectorization.
    Contains a 20-30 word summary of visual, interaction, behavioral, and persona traits.
    """
    vibe_summary: str = "New user seeking a standard, clean experience."

    def to_vector_key(self) -> str:
        """Return the summary directly for embedding"""
        return self.vibe_summary
