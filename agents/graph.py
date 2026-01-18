"""
Main LangGraph definition for the agent orchestration
Uses parallel branches for the three-stream processing architecture
"""
from langgraph.graph import StateGraph, END, START
from typing import TypedDict, Literal, Annotated, Sequence
from operator import add
import asyncio

from agents.config import agent_config
from agents.streams.motor_state_stream import motor_state_stream
from agents.streams.context_analyst_stream import context_analyst_stream
from agents.streams.variance_auditor_stream import variance_auditor_stream
from agents.generators.stability_agent import stability_agent
from agents.generators.exploratory_agent import exploratory_agent
from agents.reducers.preference_reducer import preference_reducer
from agents.synthesizers.profile_synthesizer import profile_synthesizer


class AgentState(TypedDict):
    """State passed through the agent graph"""
    # Input data
    session_id: str
    telemetry_batch: list[dict]
    interactions: list[dict]
    loud_module_events: list[dict]
    current_preferences: dict
    
    # Stream outputs
    motor_state: str
    motor_confidence: float
    motor_metrics: dict
    context_analysis: dict
    variance_audit: dict
    
    # Reduced preferences
    updated_preferences: dict
    
    # Layout proposals
    stability_proposal: dict
    exploratory_proposal: dict
    
    # Final output - User Profile for vectorization
    user_profile: dict


def motor_state_node(state: AgentState) -> dict:
    """
    Process motor state using pure Python (Stream 1).
    Zero API cost - runs continuously at ~100ms intervals.
    """
    print("Agent Motor State working...")
    telemetry = state.get("telemetry_batch", [])
    result = motor_state_stream.process(telemetry)
    
    print(f"Agent Motor State raw response: {result}")
    print(f"Current Sentiment (Motor): {result['state']}")
    
    return {
        "motor_state": result["state"],
        "motor_confidence": result["confidence"],
        "motor_metrics": result["metrics"],
    }


async def context_analysis_node(state: AgentState) -> dict:
    """
    Context Analyst agent (Stream 2).
    Uses Backboard.io for stateful thread management.
    Runs on 5-second batch intervals.
    """
    print("Agent Context Analysis working...")
    session_id = state.get("session_id", "")
    motor_state = {
        "state": state.get("motor_state", "idle"),
        "confidence": state.get("motor_confidence", 0.0),
    }
    interactions = state.get("interactions", [])
    current_preferences = state.get("current_preferences", {})
    
    result = await context_analyst_stream.process(
        session_id=session_id,
        motor_state=motor_state,
        interactions=interactions,
        current_preferences=current_preferences,
    )
    
    print(f"Agent Context Analysis raw response: {result}")
    if "insights" in result:
        print(f"Current Sentiment (Context Insights): {result['insights']}")
    
    return {"context_analysis": result}


async def variance_audit_node(state: AgentState) -> dict:
    """
    Variance Auditor agent (Stream 3).
    Uses Backboard.io for stateful thread management.
    Analyzes engagement with "loud" A/B testing modules.
    """
    print("Agent Variance Audit working...")
    session_id = state.get("session_id", "")
    loud_events = state.get("loud_module_events", [])
    
    # Skip if no loud module events
    if not loud_events:
        print("Agent Variance Audit raw response: Skipped (no events)")
        return {"variance_audit": {"active": False, "signals": []}}
    
    baseline = {
        "avg_dwell_time": 2000,
        "avg_scroll_velocity": 300,
    }
    
    result = await variance_auditor_stream.process(
        session_id=session_id,
        loud_module_events=loud_events,
        baseline_engagement=baseline,
    )
    
    print(f"Agent Variance Audit raw response: {result}")
    
    return {"variance_audit": result}


def preference_reduction_node(state: AgentState) -> dict:
    """
    Map-Reduce: Combine outputs from all three streams.
    Updates preference weights based on aggregated signals.
    """
    print("Agent Preference Reduction working...")
    motor_state = {
        "state": state.get("motor_state", "idle"),
        "confidence": state.get("motor_confidence", 0.0),
    }
    context_analysis = state.get("context_analysis", {})
    variance_audit = state.get("variance_audit", {})
    current_preferences = state.get("current_preferences", {})
    
    updated = preference_reducer.reduce(
        motor_state=motor_state,
        context_analysis=context_analysis,
        variance_audit=variance_audit,
        current_preferences=current_preferences,
    )
    
    print(f"Agent Preference Reduction raw response: {updated}")
    
    return {"updated_preferences": updated}


async def stability_generation_node(state: AgentState) -> dict:
    """
    Stability Agent: Generate conservative, validated layout.
    Uses Backboard.io for stateful thread management.
    """
    print("Agent Stability Generation working...")
    session_id = state.get("session_id", "")
    preferences = state.get("updated_preferences", {})
    
    available_modules = _get_available_modules()
    
    result = await stability_agent.generate(
        session_id=session_id,
        preferences=preferences,
        available_modules=available_modules,
        page_type="home",
    )
    
    print(f"Agent Stability Generation raw response: {result}")
    
    return {"stability_proposal": result}


async def exploratory_generation_node(state: AgentState) -> dict:
    """
    Exploratory Agent: Generate novel layout with A/B testing modules.
    Uses Backboard.io for stateful thread management.
    """
    print("Agent Exploratory Generation working...")
    session_id = state.get("session_id", "")
    preferences = state.get("updated_preferences", {})
    
    genre_weights = preferences.get("genre_weights", {})
    all_genres = ["base", "minimalist", "neobrutalist", "glassmorphism", "loud"]
    preference_voids = [g for g in all_genres if genre_weights.get(g, 0) < 0.3]
    
    available_modules = _get_available_modules()
    
    result = await exploratory_agent.generate(
        session_id=session_id,
        preferences=preferences,
        available_modules=available_modules,
        preference_voids=preference_voids,
        page_type="home",
    )
    
    print(f"Agent Exploratory Generation raw response: {result}")
    
    return {"exploratory_proposal": result}


async def profile_synthesis_node(state: AgentState) -> dict:
    """
    Synthesize User Profile from stability and exploratory proposals.
    Uses 80/20 weighting to produce a vectorizable JSON.
    """
    print("Agent Profile Synthesis working...")
    session_id = state.get("session_id", "default_session")
    stability = state.get("stability_proposal", {})
    exploratory = state.get("exploratory_proposal", {})
    motor_state = state.get("motor_state", "idle")
    motor_confidence = state.get("motor_confidence", 0.0)
    context_analysis = state.get("context_analysis", {})
    
    user_profile = await profile_synthesizer.synthesize(
        session_id=session_id,
        stability_proposal=stability,
        exploratory_proposal=exploratory,
        motor_state=motor_state,
        motor_confidence=motor_confidence,
        context_analysis=context_analysis,
    )
    
    print(f"Agent Profile Synthesis raw response: {user_profile}")
    
    return {"user_profile": user_profile}


def _get_available_modules() -> list[dict]:
    """Get list of available UI modules from registry"""
    # Placeholder - in production, this would read from component registry
    return [
        {"id": "hero-base", "type": "hero", "genre": "base"},
        {"id": "hero-minimalist", "type": "hero", "genre": "minimalist"},
        {"id": "grid-base", "type": "product-grid", "genre": "base"},
        {"id": "grid-neobrutalist", "type": "product-grid", "genre": "neobrutalist"},
        {"id": "banner-glassmorphism", "type": "banner", "genre": "glassmorphism"},
        {"id": "cta-loud", "type": "cta", "genre": "loud", "is_loud": True},
    ]


def create_agent_graph() -> StateGraph:
    """
    Create the main agent orchestration graph.
    
    Flow:
    1. Motor state analysis (parallel with context/variance)
    2. Context analysis (parallel with motor/variance)  
    3. Variance audit (parallel with motor/context)
    4. Preference reduction (combines all streams)
    5. Stability generation (parallel with exploratory)
    6. Exploratory generation (parallel with stability)
    7. Profile synthesis (80/20 weighted merge -> vectorizable JSON)
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("motor_state", motor_state_node)
    workflow.add_node("context_analysis", context_analysis_node)
    workflow.add_node("variance_audit", variance_audit_node)
    workflow.add_node("preference_reduction", preference_reduction_node)
    workflow.add_node("stability_generation", stability_generation_node)
    workflow.add_node("exploratory_generation", exploratory_generation_node)
    workflow.add_node("profile_synthesis", profile_synthesis_node)
    
    # Entry: Start all three streams
    workflow.add_edge(START, "motor_state")
    workflow.add_edge(START, "context_analysis")
    workflow.add_edge(START, "variance_audit")
    
    # All streams feed into reduction
    workflow.add_edge("motor_state", "preference_reduction")
    workflow.add_edge("context_analysis", "preference_reduction")
    workflow.add_edge("variance_audit", "preference_reduction")
    
    # Reduction triggers parallel generation
    workflow.add_edge("preference_reduction", "stability_generation")
    workflow.add_edge("preference_reduction", "exploratory_generation")
    
    # Both generators feed into profile synthesis
    workflow.add_edge("stability_generation", "profile_synthesis")
    workflow.add_edge("exploratory_generation", "profile_synthesis")
    
    # Profile synthesis is final
    workflow.add_edge("profile_synthesis", END)
    
    return workflow.compile()


# Create the compiled graph instance
agent_graph = create_agent_graph()


async def run_layout_generation(
    session_id: str,
    telemetry_batch: list[dict],
    interactions: list[dict],
    loud_module_events: list[dict],
    current_preferences: dict,
) -> dict:
    """
    Run the full layout generation pipeline.
    
    Args:
        session_id: User session identifier
        telemetry_batch: Recent mouse/touch telemetry events
        interactions: Recent UI interactions (clicks, hovers)
        loud_module_events: Interactions with A/B testing modules
        current_preferences: Current preference weights
        
    Returns:
        User Profile JSON for vectorization and module matching
    """
    initial_state: AgentState = {
        "session_id": session_id,
        "telemetry_batch": telemetry_batch,
        "interactions": interactions,
        "loud_module_events": loud_module_events,
        "current_preferences": current_preferences,
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
    
    result = await agent_graph.ainvoke(initial_state)
    return result.get("user_profile", {})

