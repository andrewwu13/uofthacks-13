"""
Preference Reducer - Combines outputs from all three streams
"""
from typing import Dict, List


class PreferenceReducer:
    """
    Reduces outputs from motor state, context analyst, and variance auditor
    into a unified JSON directive for layout generation.
    """
    
    def reduce(
        self,
        motor_state: dict,
        context_analysis: dict,
        variance_audit: dict,
        current_preferences: dict,
    ) -> dict:
        """
        Combine stream outputs into unified preference directive.
        
        Args:
            motor_state: Output from motor state stream
            context_analysis: Output from context analyst stream
            variance_audit: Output from variance auditor stream
            current_preferences: Current user preferences
            
        Returns:
            Unified preference directive for layout generation
        """
        # Start with current preferences
        updated_preferences = dict(current_preferences)
        
        # Apply context analysis updates
        preference_updates = context_analysis.get("preference_updates", {})
        for genre, delta in preference_updates.items():
            current = updated_preferences.get("genre_weights", {}).get(genre, 0.2)
            updated_preferences.setdefault("genre_weights", {})[genre] = min(1.0, max(0.0, current + delta))
        
        # Apply variance audit signals
        for signal in variance_audit.get("signals", []):
            genre = signal.get("genre")
            reward = signal.get("reward", 0)
            if genre:
                current = updated_preferences.get("genre_weights", {}).get(genre, 0.2)
                # Apply reward with learning rate
                updated_preferences.setdefault("genre_weights", {})[genre] = min(1.0, max(0.0, current + reward * 0.1))
        
        # Adjust based on motor state
        motor_state_adjustments = self._motor_state_to_preference(motor_state.get("state", "idle"))
        for key, value in motor_state_adjustments.items():
            updated_preferences[key] = value
        
        # Calculate overall confidence
        updated_preferences["interaction_confidence"] = self._calculate_confidence(
            motor_state.get("confidence", 0),
            context_analysis.get("confidence", 0),
            variance_audit.get("signals", []),
        )
        
        return updated_preferences
    
    def _motor_state_to_preference(self, state: str) -> dict:
        """Convert motor state to preference adjustments"""
        adjustments = {}
        
        if state == "anxious" or state == "jittery":
            # User seems overwhelmed - prefer simpler layouts
            adjustments["interaction_style"] = "minimalist"
        elif state == "determined":
            # User knows what they want - show more options
            adjustments["interaction_style"] = "detailed"
        
        return adjustments
    
    def _calculate_confidence(
        self,
        motor_confidence: float,
        context_confidence: float,
        signals: List[dict],
    ) -> float:
        """Calculate overall confidence score"""
        signal_confidence = len(signals) * 0.1 if signals else 0
        return min(1.0, (motor_confidence + context_confidence + signal_confidence) / 3)


preference_reducer = PreferenceReducer()
