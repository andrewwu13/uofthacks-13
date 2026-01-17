"""
Global constants
"""

# Module genres
GENRES = ["base", "minimalist", "neobrutalist", "glassmorphism", "loud"]

# Module types
MODULE_TYPES = [
    "hero",
    "product-grid",
    "product-card",
    "banner",
    "testimonial",
    "cta",
    "feature-list",
]

# Motor states
MOTOR_STATES = ["idle", "determined", "browsing", "anxious", "jittery"]

# Device types
DEVICE_TYPES = ["desktop", "mobile", "tablet"]

# Page types
PAGE_TYPES = ["home", "product", "category", "search", "cart", "checkout"]

# Cache TTLs (seconds)
CACHE_TTL_MOTOR_STATE = 60
CACHE_TTL_PREFERENCES = 3600
CACHE_TTL_LAYOUT = 300
CACHE_TTL_PRODUCTS = 600

# Agent intervals (milliseconds)
MOTOR_STATE_INTERVAL_MS = 100
CONTEXT_ANALYST_INTERVAL_MS = 5000
VARIANCE_AUDITOR_INTERVAL_MS = 5000
