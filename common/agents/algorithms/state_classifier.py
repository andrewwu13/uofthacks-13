"""
State Classifier - Percentile-aware classification using new motor metrics
Pure Python implementation for zero API cost

Improvements over v1:
- Uses p50/p90 velocity instead of avg_velocity (immune to dwell skew)
- New `dwell_focused` state for high-engagement / long-stop sessions
- Returns a human-readable `motor_summary` dict for direct prompt injection
"""

from typing import Tuple, Literal, Dict
from agents.config import agent_config

MotorState = Literal["idle", "determined", "browsing", "dwell_focused", "anxious", "jittery"]


class StateClassifier:
    """
    Classifies user cognitive state based on motor metrics.

    Uses percentile-based velocity (p50/p90) rather than averages so that
    a long dwell phase does not pull down the dominant movement signal.
    """

    def __init__(self):
        self.jitter_threshold = agent_config.jitter_threshold
        self.anxiety_threshold = agent_config.anxiety_threshold
        self.determined_velocity = agent_config.determined_velocity_threshold

    def classify(self, metrics: dict) -> Tuple[MotorState, float]:
        """
        Classify cognitive state from rich motor metrics.

        Uses p50/p90 velocity — robust against phases that inflate/deflate averages.

        Args:
            metrics: Motion metrics from the updated MotorAnalyzer

        Returns:
            Tuple of (state, confidence)
        """
        p50 = metrics.get("p50_velocity", metrics.get("avg_velocity", 0))
        p90 = metrics.get("p90_velocity", metrics.get("max_velocity", 0))
        direction_change_rate = metrics.get("direction_change_rate", 0)
        avg_jerk = metrics.get("avg_jerk", 0)
        dwell_fraction = metrics.get("dwell_fraction", 0)
        dwell_count = metrics.get("dwell_count", 0)

        # Idle: virtually no movement across the whole batch
        if p90 < 15:
            return ("idle", 0.95)

        # Dwell-focused: significant portion of time spent stopped, multiple stops
        # This is the key new state — replaces the "anxious" misclassification
        # for users who scroll fast then stop to examine specific elements.
        if dwell_fraction > 0.35 and dwell_count >= 1:
            confidence = min(1.0, dwell_fraction * 1.5)
            return ("dwell_focused", round(confidence, 2))

        # Jittery: high direction reversals + high jerk + slow p50
        # (genuine nervous cursor movement, not dwell)
        if (
            direction_change_rate > self.jitter_threshold
            and avg_jerk > 1000
            and p50 < 150
        ):
            confidence = min(1.0, direction_change_rate / self.jitter_threshold)
            return ("jittery", round(confidence, 2))

        # Anxious: moderate direction changes (indecision without jitter)
        if direction_change_rate > self.anxiety_threshold and p50 < 300:
            confidence = min(1.0, direction_change_rate / self.jitter_threshold)
            return ("anxious", round(confidence, 2))

        # Determined: fast p90, smooth trajectory (low direction changes)
        if p90 > self.determined_velocity and direction_change_rate < 0.1:
            confidence = min(1.0, p90 / (self.determined_velocity * 2))
            return ("determined", round(confidence, 2))

        # Default: general browsing
        return ("browsing", 0.7)

    def build_motor_summary(self, state: MotorState, confidence: float, metrics: dict) -> Dict:
        """
        Build a human-readable summary dict for prompt injection.
        Keys match the {metrics} variable slot in data_cleaner.txt.
        """
        return {
            "state": state,
            "confidence_pct": round(confidence * 100),
            "total_duration_ms": metrics.get("total_duration_ms", 0),
            "sample_count": metrics.get("sample_count", 0),
            "p50_velocity": metrics.get("p50_velocity", 0),
            "p90_velocity": metrics.get("p90_velocity", 0),
            "peak_velocity": metrics.get("peak_velocity", 0),
            "dwell_count": metrics.get("dwell_count", 0),
            "avg_dwell_ms": metrics.get("avg_dwell_ms", 0),
            "dwell_fraction_pct": round(metrics.get("dwell_fraction", 0) * 100),
            "direction_changes": metrics.get("direction_changes", 0),
            "direction_change_rate_pct": round(metrics.get("direction_change_rate", 0) * 100),
            "click_impulse_score": metrics.get("click_impulse_score", 0),
        }

    def get_thresholds(self) -> dict:
        """Return current thresholds for debugging."""
        return {
            "jitter_threshold": self.jitter_threshold,
            "anxiety_threshold": self.anxiety_threshold,
            "determined_velocity": self.determined_velocity,
        }
