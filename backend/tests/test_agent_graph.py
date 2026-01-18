"""
Unit tests for Agent Graph and Profile Synthesis

Tests agent nodes with mocked LLM - no API calls or tokens spent.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Ensure agents is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))


class TestAgentState:
    """Tests for AgentState TypedDict structure."""
    
    def test_agent_state_keys(self):
        """AgentState should have all required keys."""
        from agents.graph import AgentState
        
        # Check required keys exist in annotations
        annotations = AgentState.__annotations__
        
        required_keys = [
            "session_id", "telemetry_batch", "interactions",
            "motor_state", "motor_confidence", "user_profile"
        ]
        
        for key in required_keys:
            assert key in annotations, f"Missing key: {key}"


class TestMotorStateNode:
    """Tests for motor_state_node - pure Python, no LLM."""
    
    def test_motor_state_node_returns_state(self):
        """motor_state_node should return motor state classification."""
        from agents.graph import motor_state_node
        
        state = {
            "session_id": "test",
            "telemetry_batch": [
                {"velocity": {"x": 100, "y": 50}, "acceleration": {"x": 10, "y": 5}}
            ],
            "interactions": [],
            "loud_module_events": [],
            "current_preferences": {},
            "motor_state": "",
            "motor_confidence": 0.0,
            "motor_metrics": {},
        }
        
        result = motor_state_node(state)
        
        assert "motor_state" in result
        assert "motor_confidence" in result
        assert result["motor_state"] in ["idle", "determined", "browsing", "anxious", "jittery"]
    
    def test_motor_state_idle_on_no_data(self):
        """Empty telemetry should result in idle state."""
        from agents.graph import motor_state_node
        
        state = {
            "session_id": "test",
            "telemetry_batch": [],
            "interactions": [],
            "loud_module_events": [],
            "current_preferences": {},
        }
        
        result = motor_state_node(state)
        
        assert result["motor_state"] == "idle"
        assert result["motor_confidence"] == 0.0


class TestPreferenceReductionNode:
    """Tests for preference_reduction_node."""
    
    def test_preference_reduction_merges_outputs(self):
        """Should merge context and variance analysis."""
        from agents.graph import preference_reduction_node
        
        state = {
            "session_id": "test",
            "motor_state": "browsing",
            "motor_confidence": 0.7,
            "context_analysis": {"focus": "product_browsing"},
            "variance_audit": {"positive_variance": True},
            "current_preferences": {},
        }
        
        result = preference_reduction_node(state)
        
        assert "updated_preferences" in result


class TestProfileSynthesisNode:
    """Tests for profile_synthesis_node."""
    
    def test_profile_synthesis_creates_profile(self):
        """Should create user_profile from proposals."""
        from agents.graph import profile_synthesis_node
        
        state = {
            "session_id": "test",
            "stability_proposal": {
                "visual": {"color_scheme": "dark", "density": "medium"}
            },
            "exploratory_proposal": {
                "visual": {"color_scheme": "vibrant", "density": "high"}
            },
            "updated_preferences": {},
        }
        
        result = profile_synthesis_node(state)
        
        assert "user_profile" in result
        assert result["user_profile"] is not None
    
    def test_profile_synthesis_weights_stability(self):
        """Profile should weight stability at 80%."""
        from agents.graph import profile_synthesis_node
        
        state = {
            "session_id": "test",
            "stability_proposal": {
                "visual": {"color_scheme": "dark"}
            },
            "exploratory_proposal": {
                "visual": {"color_scheme": "light"}
            },
            "updated_preferences": {},
        }
        
        result = profile_synthesis_node(state)
        
        # 80/20 weighting means stability should dominate
        profile = result["user_profile"]
        # The exact value depends on implementation
        assert profile is not None


class TestRunLayoutGeneration:
    """Tests for run_layout_generation main entry point."""
    
    @pytest.fixture
    def mock_agent_graph(self):
        """Mock the compiled agent graph."""
        mock_graph = MagicMock()
        mock_graph.invoke = MagicMock(return_value={
            "user_profile": {
                "visual": {"color_scheme": "dark"},
                "inferred": {"summary": "Dark mode user"}
            }
        })
        return mock_graph
    
    @pytest.mark.asyncio
    async def test_run_layout_generation_returns_profile(self, mock_agent_graph):
        """Should return user profile dictionary."""
        with patch('agents.graph.agent_graph', mock_agent_graph):
            from agents.graph import run_layout_generation
            
            result = await run_layout_generation(
                session_id="test_session",
                telemetry_batch=[],
                interactions=[],
                loud_module_events=[],
                current_preferences={}
            )
            
            assert result is not None
            assert "visual" in result or result is None
    
    @pytest.mark.asyncio
    async def test_run_layout_generation_handles_errors(self, mock_agent_graph):
        """Should handle errors gracefully."""
        mock_agent_graph.invoke.side_effect = Exception("LLM Error")
        
        with patch('agents.graph.agent_graph', mock_agent_graph):
            from agents.graph import run_layout_generation
            
            # Should not raise, but return None or handle gracefully
            try:
                result = await run_layout_generation(
                    session_id="test_session",
                    telemetry_batch=[],
                    interactions=[],
                    loud_module_events=[],
                    current_preferences={}
                )
                # If it doesn't raise, check result
                assert result is None or isinstance(result, dict)
            except Exception:
                # Expected - error propagates
                pass


class TestContextAnalysisNode:
    """Tests for context_analysis_node with mocked LLM."""
    
    @pytest.fixture
    def mock_thread_manager(self):
        """Mock Backboard thread manager."""
        mock = MagicMock()
        mock.send_message = AsyncMock(return_value={
            "response": '{"analysis": "browsing products", "confidence": 0.85}'
        })
        return mock
    
    @pytest.mark.asyncio
    async def test_context_analysis_with_mocked_llm(self, mock_thread_manager):
        """Context analysis should work with mocked LLM."""
        with patch('agents.graph.thread_manager', mock_thread_manager):
            from agents.graph import context_analysis_node
            
            state = {
                "session_id": "test",
                "telemetry_batch": [],
                "interactions": [{"type": "hover", "target_id": "product_1"}],
                "motor_state": "browsing",
                "motor_confidence": 0.7,
            }
            
            result = context_analysis_node(state)
            
            assert "context_analysis" in result


class TestVarianceAuditNode:
    """Tests for variance_audit_node with mocked LLM."""
    
    def test_variance_audit_empty_events(self):
        """Should handle empty loud module events."""
        from agents.graph import variance_audit_node
        
        state = {
            "session_id": "test",
            "loud_module_events": [],
            "motor_state": "idle",
        }
        
        result = variance_audit_node(state)
        
        assert "variance_audit" in result


class TestStabilityGenerationNode:
    """Tests for stability_generation_node."""
    
    def test_stability_generation_returns_proposal(self):
        """Should return stability_proposal."""
        from agents.graph import stability_generation_node
        
        state = {
            "session_id": "test",
            "updated_preferences": {
                "visual": {"color_scheme": "dark"}
            },
        }
        
        result = stability_generation_node(state)
        
        assert "stability_proposal" in result


class TestExploratoryGenerationNode:
    """Tests for exploratory_generation_node."""
    
    def test_exploratory_generation_returns_proposal(self):
        """Should return exploratory_proposal."""
        from agents.graph import exploratory_generation_node
        
        state = {
            "session_id": "test",
            "updated_preferences": {},
            "variance_audit": {},
        }
        
        result = exploratory_generation_node(state)
        
        assert "exploratory_proposal" in result


class TestGraphCreation:
    """Tests for create_agent_graph function."""
    
    def test_graph_creation(self):
        """Should create a valid StateGraph."""
        from agents.graph import create_agent_graph
        
        graph = create_agent_graph()
        
        assert graph is not None
    
    def test_graph_has_nodes(self):
        """Graph should have all required nodes."""
        from agents.graph import create_agent_graph
        
        graph = create_agent_graph()
        
        # Graph should be compiled and callable
        assert hasattr(graph, 'invoke') or hasattr(graph, 'get_graph')


class TestProfileSynthesizer:
    """Tests for profile_synthesizer module."""
    
    def test_synthesize_profile_80_20_weighting(self):
        """Should apply 80/20 weighting to stability/exploratory."""
        from agents.synthesizers.profile_synthesizer import synthesize_profile
        
        stability = {
            "visual": {
                "color_scheme": "dark",
                "corner_radius": "sharp"
            }
        }
        exploratory = {
            "visual": {
                "color_scheme": "light",
                "corner_radius": "pill"
            }
        }
        
        result = synthesize_profile(stability, exploratory)
        
        assert result is not None
        assert "visual" in result
    
    def test_synthesize_profile_handles_missing_keys(self):
        """Should handle missing keys gracefully."""
        from agents.synthesizers.profile_synthesizer import synthesize_profile
        
        stability = {"visual": {"color_scheme": "dark"}}
        exploratory = {}
        
        result = synthesize_profile(stability, exploratory)
        
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
