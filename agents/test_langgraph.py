#!/usr/bin/env python3
"""
Test script to verify LangGraph setup
Run with: python test_langgraph.py
"""
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.graph import agent_graph, run_layout_generation, AgentState


async def test_basic_graph():
    """Test that the graph can be invoked"""
    print("Testing LangGraph setup...")
    print("-" * 50)
    
    # Create minimal test state
    initial_state: AgentState = {
        "session_id": "test-session-123",
        "telemetry_batch": [
            {"timestamp": 1000, "x": 100, "y": 100, "velocity": {"x": 50, "y": 30}, "acceleration": {"x": 5, "y": 3}},
            {"timestamp": 1100, "x": 150, "y": 130, "velocity": {"x": 500, "y": 300}, "acceleration": {"x": 50, "y": 30}},
        ],
        "interactions": [
            {"type": "hover", "module_id": "hero-1", "genre": "minimalist", "duration": 2500},
        ],
        "loud_module_events": [],
        "current_preferences": {
            "genre_weights": {
                "base": 0.2,
                "minimalist": 0.3,
                "neobrutalist": 0.15,
                "glassmorphism": 0.2,
                "loud": 0.15,
            }
        },
        "motor_state": "idle",
        "motor_confidence": 0.0,
        "motor_metrics": {},
        "context_analysis": {},
        "variance_audit": {},
        "updated_preferences": {},
        "stability_proposal": {},
        "exploratory_proposal": {},
        "final_layout": {},
    }
    
    print("✓ Graph created successfully")
    print(f"  Nodes: {list(agent_graph.nodes.keys())}")
    
    # Test motor state node directly
    from agents.streams.motor_state_stream import motor_state_stream
    motor_result = motor_state_stream.process(initial_state["telemetry_batch"])
    print(f"✓ Motor state stream works: state={motor_result['state']}, confidence={motor_result['confidence']:.2f}")
    
    # Test preference reducer
    from agents.reducers.preference_reducer import preference_reducer
    reduced = preference_reducer.reduce(
        motor_state={"state": motor_result["state"], "confidence": motor_result["confidence"]},
        context_analysis={"preference_updates": {"minimalist": 0.05}},
        variance_audit={"signals": []},
        current_preferences=initial_state["current_preferences"],
    )
    print(f"✓ Preference reducer works: confidence={reduced.get('interaction_confidence', 0):.2f}")
    
    print("-" * 50)
    print("LangGraph setup verified successfully!")
    print("\nNote: Full async graph invocation requires OpenAI API key for LLM nodes.")
    print("Set OPENAI_API_KEY environment variable to test full pipeline.")


async def test_full_pipeline():
    """Test the full pipeline (requires OpenAI API key)"""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\nSkipping full pipeline test (OPENAI_API_KEY not set)")
        return
    
    print("\nTesting full pipeline with LLM...")
    result = await run_layout_generation(
        session_id="test-session-123",
        telemetry_batch=[
            {"timestamp": 1000, "x": 100, "y": 100, "velocity": {"x": 50, "y": 30}, "acceleration": {"x": 5, "y": 3}},
        ],
        interactions=[
            {"type": "hover", "module_id": "hero-1", "genre": "minimalist", "duration": 2500},
        ],
        loud_module_events=[],
        current_preferences={"genre_weights": {"minimalist": 0.3}},
    )
    
    print(f"✓ Full pipeline completed!")
    print(f"  Layout version: {result.get('version')}")
    print(f"  Sections: {len(result.get('sections', []))}")


if __name__ == "__main__":
    asyncio.run(test_basic_graph())
    asyncio.run(test_full_pipeline())
