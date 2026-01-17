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
    
    # Final output
    final_layout: dict


def motor_state_node(state: AgentState) -> dict:
    """
    Process motor state using pure Python (Stream 1).
    Zero API cost - runs continuously at ~100ms intervals.
    """
    telemetry = state.get("telemetry_batch", [])
    result = motor_state_stream.process(telemetry)
    
    return {
        "motor_state": result["state"],
        "motor_confidence": result["confidence"],
        "motor_metrics": result["metrics"],
    }


async def context_analysis_node(state: AgentState) -> dict:
    """
    Context Analyst agent (Stream 2).
    Uses fast LLM to correlate motor state with UI interactions.
    Runs on 5-second batch intervals.
    """
    motor_state = {
        "state": state.get("motor_state", "idle"),
        "confidence": state.get("motor_confidence", 0.0),
    }
    interactions = state.get("interactions", [])
    current_preferences = state.get("current_preferences", {})
    
    result = await context_analyst_stream.process(
        motor_state=motor_state,
        interactions=interactions,
        current_preferences=current_preferences,
    )
    
    return {"context_analysis": result}


async def variance_audit_node(state: AgentState) -> dict:
    """
    Variance Auditor agent (Stream 3).
    Analyzes engagement with "loud" A/B testing modules.
    Runs on 5-second batch intervals.
    """
    loud_events = state.get("loud_module_events", [])
    
    # Skip if no loud module events
    if not loud_events:
        return {"variance_audit": {"active": False, "signals": []}}
    
    baseline = {
        "avg_dwell_time": 2000,  # Default baseline
        "avg_scroll_velocity": 300,
    }
    
    result = await variance_auditor_stream.process(
        loud_module_events=loud_events,
        baseline_engagement=baseline,
    )
    
    return {"variance_audit": result}


def preference_reduction_node(state: AgentState) -> dict:
    """
    Map-Reduce: Combine outputs from all three streams.
    Updates preference weights based on aggregated signals.
    """
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
    
    return {"updated_preferences": updated}


async def stability_generation_node(state: AgentState) -> dict:
    """
    Stability Agent: Generate conservative, validated layout.
    Uses 70% confidence threshold for module selection.
    """
    preferences = state.get("updated_preferences", {})
    
    # Get available modules (would come from registry in production)
    available_modules = _get_available_modules()
    
    result = await stability_agent.generate(
        preferences=preferences,
        available_modules=available_modules,
        page_type="home",
    )
    
    return {"stability_proposal": result}


async def exploratory_generation_node(state: AgentState) -> dict:
    """
    Exploratory Agent: Generate novel layout with A/B testing modules.
    Higher temperature, probes untested aesthetic territories.
    """
    preferences = state.get("updated_preferences", {})
    
    # Find genres not yet tested
    genre_weights = preferences.get("genre_weights", {})
    all_genres = ["base", "minimalist", "neobrutalist", "glassmorphism", "loud"]
    preference_voids = [g for g in all_genres if genre_weights.get(g, 0) < 0.3]
    
    available_modules = _get_available_modules()
    
    result = await exploratory_agent.generate(
        preferences=preferences,
        available_modules=available_modules,
        preference_voids=preference_voids,
        page_type="home",
    )
    
    return {"exploratory_proposal": result}


def layout_synthesis_node(state: AgentState) -> dict:
    """
    Synthesize final layout from stability and exploratory proposals.
    Balances safe choices with novel testing modules.
    """
    stability = state.get("stability_proposal", {})
    exploratory = state.get("exploratory_proposal", {})
    preferences = state.get("updated_preferences", {})
    
    # Merge proposals: Use stability as base, inject exploratory loud modules
    final_sections = stability.get("sections", [])
    
    # Add 1-2 loud modules from exploratory proposal
    exploratory_sections = exploratory.get("sections", [])
    for section in exploratory_sections:
        for module in section.get("modules", []):
            if module.get("is_loud"):
                # Insert loud module into a safe position
                if final_sections:
                    final_sections[-1].setdefault("modules", []).append(module)
                break  # Only add one loud module per synthesis
    
    # Apply design token mutations if suggested
    design_tokens = exploratory.get("token_mutations", {})
    
    return {
        "final_layout": {
            "version": "1.0.0",
            "session_id": state.get("session_id", ""),
            "sections": final_sections,
            "design_tokens": design_tokens,
            "preferences_snapshot": preferences,
        }
    }


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
    7. Layout synthesis (final merge)
    """
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("motor_state", motor_state_node)
    workflow.add_node("context_analysis", context_analysis_node)
    workflow.add_node("variance_audit", variance_audit_node)
    workflow.add_node("preference_reduction", preference_reduction_node)
    workflow.add_node("stability_generation", stability_generation_node)
    workflow.add_node("exploratory_generation", exploratory_generation_node)
    workflow.add_node("layout_synthesis", layout_synthesis_node)
    
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
    
    # Both generators feed into synthesis
    workflow.add_edge("stability_generation", "layout_synthesis")
    workflow.add_edge("exploratory_generation", "layout_synthesis")
    
    # Synthesis is final
    workflow.add_edge("layout_synthesis", END)
    
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
        Generated layout directive
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
        "final_layout": {},
    }
    
    result = await agent_graph.ainvoke(initial_state)
    return result.get("final_layout", {})
