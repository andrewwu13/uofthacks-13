"""
Stream 1: High-frequency motor state analysis (pure Python, no LLM)
Runs near-constantly for zero API cost
"""
from typing import Literal
from agents.algorithms.motor_analyzer import MotorAnalyzer
from agents.algorithms.state_classifier import StateClassifier


MotorState = Literal["idle", "determined", "browsing", "anxious", "jittery"]


class MotorStateStream:
    """
    High-frequency neurological layer.
    Computes velocity (1st derivative) and acceleration (2nd derivative)
    of cursor/touch input to model user's cognitive state.
    """
    
    def __init__(self):
        self.analyzer = MotorAnalyzer()
        self.classifier = StateClassifier()
    
    def process(self, telemetry_batch: list[dict]) -> dict:
        """
        Process a batch of motor telemetry events.
        
        Args:
            telemetry_batch: List of mouse/touch telemetry events
            
        Returns:
            Motor state analysis result
        """
        if not telemetry_batch:
            return {
                "state": "idle",
                "confidence": 0.0,
                "metrics": {},
            }
        
        # Calculate motion metrics
        metrics = self.analyzer.analyze(telemetry_batch)
        
        # Classify state based on metrics
        state, confidence = self.classifier.classify(metrics)
        
        return {
            "state": state,
            "confidence": confidence,
            "metrics": metrics,
        }


motor_state_stream = MotorStateStream()
