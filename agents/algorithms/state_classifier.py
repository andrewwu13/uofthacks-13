"""
State Classifier - Threshold-based classification of cognitive state
Pure Python implementation for zero API cost
"""
from typing import Tuple, Literal
from agents.config import agent_config


MotorState = Literal["idle", "determined", "browsing", "anxious", "jittery"]


class StateClassifier:
    """
    Classifies user cognitive state based on motion metrics.
    Uses configurable thresholds for classification.
    """
    
    def __init__(self):
        self.jitter_threshold = agent_config.jitter_threshold
        self.anxiety_threshold = agent_config.anxiety_threshold
        self.determined_velocity = agent_config.determined_velocity_threshold
    
    def classify(self, metrics: dict) -> Tuple[MotorState, float]:
        """
        Classify cognitive state from motion metrics.
        
        Args:
            metrics: Motion metrics from MotorAnalyzer
            
        Returns:
            Tuple of (state, confidence)
        """
        avg_velocity = metrics.get("avg_velocity", 0)
        direction_change_rate = metrics.get("direction_change_rate", 0)
        avg_jerk = metrics.get("avg_jerk", 0)
        
        # Idle: Very low velocity
        if avg_velocity < 10:
            return ("idle", 0.9)
        
        # Jittery: High direction changes + high jerk + low velocity
        if direction_change_rate > self.jitter_threshold and avg_jerk > 1000 and avg_velocity < 200:
            confidence = min(1.0, direction_change_rate / self.jitter_threshold)
            return ("jittery", confidence)
        
        # Anxious: Moderate direction changes + medium velocity
        if direction_change_rate > self.anxiety_threshold:
            confidence = min(1.0, direction_change_rate / self.jitter_threshold)
            return ("anxious", confidence)
        
        # Determined: High velocity, smooth movement
        if avg_velocity > self.determined_velocity and direction_change_rate < 0.1:
            confidence = min(1.0, avg_velocity / (self.determined_velocity * 2))
            return ("determined", confidence)
        
        # Default: Browsing
        return ("browsing", 0.7)
    
    def get_thresholds(self) -> dict:
        """Return current thresholds for debugging"""
        return {
            "jitter_threshold": self.jitter_threshold,
            "anxiety_threshold": self.anxiety_threshold,
            "determined_velocity": self.determined_velocity,
        }
