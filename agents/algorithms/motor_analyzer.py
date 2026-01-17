"""
Motor Analyzer - Calculates velocity, acceleration, and jerk from telemetry
Pure Python implementation for zero API cost
"""
import math
from typing import List, Dict


class MotorAnalyzer:
    """
    Analyzes cursor/touch motion using calculus.
    Computes derivatives to model cognitive state.
    """
    
    def analyze(self, telemetry: List[Dict]) -> Dict:
        """
        Analyze motion telemetry.
        
        Args:
            telemetry: List of position/velocity data points
            
        Returns:
            Motion metrics including velocity, acceleration, jerk
        """
        if len(telemetry) < 2:
            return self._empty_metrics()
        
        velocities = []
        accelerations = []
        jerks = []
        direction_changes = 0
        
        for i in range(1, len(telemetry)):
            prev = telemetry[i - 1]
            curr = telemetry[i]
            
            dt = (curr.get("timestamp", 0) - prev.get("timestamp", 0)) / 1000  # ms to s
            if dt <= 0:
                continue
            
            # Calculate velocity magnitude
            vel = curr.get("velocity", {"x": 0, "y": 0})
            vel_magnitude = math.sqrt(vel.get("x", 0) ** 2 + vel.get("y", 0) ** 2)
            velocities.append(vel_magnitude)
            
            # Calculate acceleration magnitude
            acc = curr.get("acceleration", {"x": 0, "y": 0})
            acc_magnitude = math.sqrt(acc.get("x", 0) ** 2 + acc.get("y", 0) ** 2)
            accelerations.append(acc_magnitude)
            
            # Calculate jerk (derivative of acceleration)
            if len(accelerations) >= 2:
                jerk = abs(accelerations[-1] - accelerations[-2]) / dt
                jerks.append(jerk)
            
            # Count direction changes (indicates indecision)
            if i >= 2:
                prev_vel = telemetry[i - 1].get("velocity", {"x": 0, "y": 0})
                if (prev_vel.get("x", 0) * vel.get("x", 0) < 0 or 
                    prev_vel.get("y", 0) * vel.get("y", 0) < 0):
                    direction_changes += 1
        
        return {
            "avg_velocity": sum(velocities) / len(velocities) if velocities else 0,
            "max_velocity": max(velocities) if velocities else 0,
            "avg_acceleration": sum(accelerations) / len(accelerations) if accelerations else 0,
            "max_acceleration": max(accelerations) if accelerations else 0,
            "avg_jerk": sum(jerks) / len(jerks) if jerks else 0,
            "max_jerk": max(jerks) if jerks else 0,
            "direction_changes": direction_changes,
            "direction_change_rate": direction_changes / len(telemetry) if telemetry else 0,
            "sample_count": len(telemetry),
        }
    
    def _empty_metrics(self) -> Dict:
        return {
            "avg_velocity": 0,
            "max_velocity": 0,
            "avg_acceleration": 0,
            "max_acceleration": 0,
            "avg_jerk": 0,
            "max_jerk": 0,
            "direction_changes": 0,
            "direction_change_rate": 0,
            "sample_count": 0,
        }
