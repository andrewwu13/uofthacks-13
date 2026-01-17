"""
Common utility functions
"""
import hashlib
import json
import uuid
from datetime import datetime


def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())


def generate_short_id() -> str:
    """Generate a short unique ID"""
    return uuid.uuid4().hex[:8]


def hash_dict(data: dict) -> str:
    """Generate MD5 hash of a dictionary"""
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()


def now_timestamp() -> int:
    """Get current Unix timestamp in milliseconds"""
    return int(datetime.now().timestamp() * 1000)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max"""
    return max(min_val, min(max_val, value))


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    """Normalize weights to sum to 1.0"""
    total = sum(weights.values())
    if total == 0:
        return weights
    return {k: v / total for k, v in weights.items()}
