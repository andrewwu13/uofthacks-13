"""
Stream 1: High-frequency motor state analysis (pure Python, no LLM)
Runs near-constantly for zero API cost
"""

from typing import Literal
from agents.algorithms.motor_analyzer import MotorAnalyzer
from agents.algorithms.state_classifier import StateClassifier

MotorState = Literal["idle", "determined", "browsing", "dwell_focused", "anxious", "jittery"]


class MotorStateStream:
    """
    High-frequency neurological layer.
    Computes velocity (1st derivative) and acceleration (2nd derivative)
    of cursor/touch input to model user's motor engagement state.

    The classifier attribute is exposed publicly so the graph node
    can call build_motor_summary() after classification.
    """

    def __init__(self):
        self.analyzer = MotorAnalyzer()
        self.classifier = StateClassifier()  # exposed for graph.py

    def process(self, telemetry_batch: list[dict]) -> dict:
        """
        Process a batch of motor telemetry events.

        Args:
            telemetry_batch: List of processed mouse/touch telemetry dicts
                Each: { timestamp, position:{x,y}, velocity:{x,y}, acceleration:{x,y} }

        Returns:
            dict with keys:
                state     - MotorState label
                confidence - float 0-1
                metrics   - full metrics dict from MotorAnalyzer
        """
        if not telemetry_batch:
            return {
                "state": "idle",
                "confidence": 0.0,
                "metrics": self.analyzer._empty_metrics(),
            }

        # Calculate rich motion metrics (temporal segmentation + dwell detection)
        metrics = self.analyzer.analyze(telemetry_batch)

        # Classify state using percentile-based velocity
        state, confidence = self.classifier.classify(metrics)

        return {
            "state": state,
            "confidence": confidence,
            "metrics": metrics,
        }


motor_state_stream = MotorStateStream()
