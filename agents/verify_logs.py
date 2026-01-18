import asyncio
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.graph import (
    motor_state_node,
    context_analysis_node,
    variance_audit_node,
    preference_reduction_node,
    stability_generation_node,
    exploratory_generation_node,
    profile_synthesis_node,
    AgentState
)

async def verify_logging():
    print("Running verification for logging...")
    
    # Mocking external streams to avoid API calls
    with patch('agents.streams.context_analyst_stream.context_analyst_stream.process') as mock_context, \
         patch('agents.streams.variance_auditor_stream.variance_auditor_stream.process') as mock_variance, \
         patch('agents.generators.stability_agent.stability_agent.generate') as mock_stability, \
         patch('agents.generators.exploratory_agent.exploratory_agent.generate') as mock_exploratory, \
         patch('agents.synthesizers.profile_synthesizer.profile_synthesizer.synthesize') as mock_profile:
        
        # Setup mocks
        mock_context.return_value = {"insights": "User seems anxious but interested", "preference_updates": {}}
        mock_variance.return_value = {"active": True, "signals": ["high_velocity"]}
        mock_stability.return_value = {"layout": "stable_layout"}
        mock_exploratory.return_value = {"layout": "exploratory_layout"}
        mock_profile.return_value = {"final_profile": "vector_ready"}

        # Dummy State
        state: AgentState = {
            "session_id": "test",
            "telemetry_batch": [{"timestamp": 1, "x": 0, "y": 0, "velocity": {"x": 0, "y": 0}, "acceleration": {"x": 0, "y": 0}}],
            "interactions": [],
            "loud_module_events": ["event1"],
            "current_preferences": {},
            "motor_state": "idle",
            "motor_confidence": 0.0,
            "motor_metrics": {},
            "context_analysis": {},
            "variance_audit": {},
            "updated_preferences": {},
            "stability_proposal": {},
            "exploratory_proposal": {},
            "user_profile": {},
        }
        
        print("\n--- Testing Motor State Node ---")
        motor_state_node(state)
        
        print("\n--- Testing Context Analysis Node ---")
        await context_analysis_node(state)
        
        print("\n--- Testing Variance Audit Node ---")
        await variance_audit_node(state)
        
        print("\n--- Testing Preference Reduction Node ---")
        preference_reduction_node(state)
        
        print("\n--- Testing Stability Generation Node ---")
        await stability_generation_node(state)

        print("\n--- Testing Exploratory Generation Node ---")
        await exploratory_generation_node(state)

        print("\n--- Testing Profile Synthesis Node ---")
        await profile_synthesis_node(state)

if __name__ == "__main__":
    asyncio.run(verify_logging())
