"""
Shared type definitions
"""
from typing import Literal, TypeAlias

# Type aliases
Genre: TypeAlias = Literal["base", "minimalist", "neobrutalist", "glassmorphism", "loud"]
ModuleType: TypeAlias = Literal["hero", "product-grid", "product-card", "banner", "testimonial", "cta", "feature-list"]
MotorState: TypeAlias = Literal["idle", "determined", "browsing", "anxious", "jittery"]
DeviceType: TypeAlias = Literal["desktop", "mobile", "tablet"]
PageType: TypeAlias = Literal["home", "product", "category", "search", "cart", "checkout"]
