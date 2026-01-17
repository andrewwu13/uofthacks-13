"""
Main LangGraph definition for the agent orchestration
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal
from agents.config import StreamState


class AgentState(TypedDict):
    """State passed through the agent graph"""
    session_id: str
    motor_state: str
    motor_confidence: float
    genre_weights: dict
    context_analysis: dict
    variance_audit: dict
    stability_proposal: dict
    exploratory_proposal: dict
    final_layout_directive: dict


def create_agent_graph() -> StateGraph:
    """Create the main agent orchestration graph"""
    
    workflow = StateGraph(AgentState)
    
    # Add nodes for each processing step
    workflow.add_node("motor_state_analysis", motor_state_node)
    workflow.add_node("context_analysis", context_analysis_node)
    workflow.add_node("variance_audit", variance_audit_node)
    workflow.add_node("preference_reduction", preference_reduction_node)
    workflow.add_node("stability_generation", stability_generation_node)
    workflow.add_node("exploratory_generation", exploratory_generation_node)
    workflow.add_node("layout_synthesis", layout_synthesis_node)
    
    # Define the flow
    # Parallel streams feed into reduction
    workflow.add_edge("motor_state_analysis", "preference_reduction")
    workflow.add_edge("context_analysis", "preference_reduction")
    workflow.add_edge("variance_audit", "preference_reduction")
    
    # Reduction feeds into parallel generation
    workflow.add_edge("preference_reduction", "stability_generation")
    workflow.add_edge("preference_reduction", "exploratory_generation")
    
    # Generation feeds into synthesis
    workflow.add_edge("stability_generation", "layout_synthesis")
    workflow.add_edge("exploratory_generation", "layout_synthesis")
    
    workflow.add_edge("layout_synthesis", END)
    
    # Set entry point
    workflow.set_entry_point("motor_state_analysis")
    
    return workflow.compile()


def motor_state_node(state: AgentState) -> AgentState:
    """Process motor state (pure Python, no LLM)"""
    # TODO: Import and call motor analyzer
    return state


def context_analysis_node(state: AgentState) -> AgentState:
    """Context analyst agent"""
    # TODO: Call LLM for context analysis
    return state


def variance_audit_node(state: AgentState) -> AgentState:
    """Variance auditor for loud modules"""
    # TODO: Call LLM for variance audit
    return state


def preference_reduction_node(state: AgentState) -> AgentState:
    """Reduce outputs from all streams"""
    # TODO: Combine stream outputs into unified directive
    return state


def stability_generation_node(state: AgentState) -> AgentState:
    """Stability (safe) agent for layout generation"""
    # TODO: Generate conservative layout proposal
    return state


def exploratory_generation_node(state: AgentState) -> AgentState:
    """Exploratory (risk) agent for layout generation"""
    # TODO: Generate exploratory layout proposal
    return state


def layout_synthesis_node(state: AgentState) -> AgentState:
    """Synthesize final layout from both proposals"""
    # TODO: Merge stability and exploratory proposals
    return state
