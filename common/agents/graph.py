"""
Main LangGraph definition for the agent orchestration
Reworked for Phase 1 (Cleaning) -> Phase 2 (Context Parallel) -> Phase 3 (Reduction)
"""

from langgraph.graph import StateGraph, END, START
from typing import TypedDict, List, Dict, Any
import asyncio

from agents.concurrency_manager import llm_concurrency_manager
from agents.streams.motor_state_stream import motor_state_stream
from agents.generators.data_cleaning_agent import data_cleaning_agent
from agents.generators.short_context_agent import short_context_agent
from agents.generators.long_context_agent import long_context_agent
from agents.reducers.preference_reducer import preference_reducer


class AgentState(TypedDict):
    """Refined state for the reworked flow"""

    # Input data
    session_id: str
    telemetry_batch: list[dict]
    interactions: list[dict]

    # Phase 0: Motor State (Pure Python)
    motor_state: str
    motor_metrics: dict

    # Phase 1: Data Cleaning (Lock: 1)
    behavioral_description: str

    # Phase 2: Context Analysis (Lock: 2)
    short_context_analysis: str
    long_context_analysis: str

    # Phase 3: Preference Reduction (Lock: 1)
    vibe_summary: str


def motor_state_node(state: AgentState) -> dict:
    """Stream 0: Fast motor analysis (no LLM)"""
    telemetry = state.get("telemetry_batch", [])
    result = motor_state_stream.process(telemetry)

    # Build human-readable metrics dict for the data cleaning prompt
    # This replaces the raw metrics dict with structured, labeled values
    motor_summary = motor_state_stream.classifier.build_motor_summary(
        state=result["state"],
        confidence=result["confidence"],
        metrics=result["metrics"],
    )

    return {
        "motor_state": result["state"],
        "motor_metrics": motor_summary,
    }


async def data_cleaning_node(state: AgentState) -> dict:
    """Phase 1: Objective data cleaning (Lock: 1)"""
    llm_concurrency_manager.set_limit(1)
    
    description = await data_cleaning_agent.clean(
        session_id=state["session_id"],
        motor_state=state["motor_state"],
        metrics=state["motor_metrics"],
        interactions=state["interactions"],
    )
    return {"behavioral_description": description}


async def short_context_node(state: AgentState) -> dict:
    """Phase 2A: Short-term intent analysis (Lock: 1)"""
    llm_concurrency_manager.set_limit(1)
    analysis = await short_context_agent.analyze(
        session_id=state["session_id"],
        behavioral_description=state["behavioral_description"],
    )
    return {"short_context_analysis": analysis}


async def long_context_node(state: AgentState) -> dict:
    """Phase 2B: Long-term history analysis (Lock: 1)"""
    # 1. Fetch history from MongoDB
    from app.db.mongo_client import mongo_client
    history = []
    try:
        cursor = mongo_client.db.reducer_snapshots.find(
            {"session_id": state["session_id"]}
        ).sort("timestamp", -1).limit(5)
        history = await cursor.to_list(length=5)
    except Exception as e:
        print(f"[Graph] History fetch error: {e}")

    analysis = await long_context_agent.analyze(
        session_id=state["session_id"],
        behavioral_description=state["behavioral_description"],
        history=history,
    )
    return {"long_context_analysis": analysis}


async def preference_reduction_node(state: AgentState) -> dict:
    """Phase 3: Final vibe synthesis (Lock: 1)"""
    llm_concurrency_manager.set_limit(1)
    
    summary = await preference_reducer.reduce(
        session_id=state["session_id"],
        short_context=state["short_context_analysis"],
        long_context=state["long_context_analysis"],
    )
    return {"vibe_summary": summary}


def create_agent_graph() -> StateGraph:
    """
    Reworked Graph Flow:
    Motor -> Cleaning (1) -> Short Context (1) -> Long Context (1) -> Reduction (1)
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("motor_state", motor_state_node)
    workflow.add_node("data_cleaning", data_cleaning_node)
    workflow.add_node("short_context", short_context_node)
    workflow.add_node("long_context", long_context_node)
    workflow.add_node("reduction", preference_reduction_node)

    # Sequential flow
    workflow.add_edge(START, "motor_state")
    workflow.add_edge("motor_state", "data_cleaning")
    workflow.add_edge("data_cleaning", "short_context")
    workflow.add_edge("short_context", "long_context")
    workflow.add_edge("long_context", "reduction")
    workflow.add_edge("reduction", END)

    return workflow.compile()


agent_graph = create_agent_graph()


async def run_layout_generation(
    session_id: str,
    telemetry_batch: list[dict],
    interactions: list[dict],
    **kwargs # Accept extra args but ignore for now
) -> dict:
    """
    Full pipeline entry point.
    """
    initial_state = {
        "session_id": session_id,
        "telemetry_batch": telemetry_batch,
        "interactions": interactions,
        "motor_state": "idle",
        "motor_metrics": {},
        "behavioral_description": "",
        "short_context_analysis": "",
        "long_context_analysis": "",
        "vibe_summary": "",
    }

    result = await agent_graph.ainvoke(initial_state)
    print(f"DEBUG: graph result type={type(result)}")
    
    if isinstance(result, dict):
         # Ensure vibe_summary is present in the return
         if "vibe_summary" not in result:
             result["vibe_summary"] = "Standard user experience."
         return result
    elif isinstance(result, str):
         return {"vibe_summary": result, "error": "Graph returned string instead of dict"}
    else:
         return {"vibe_summary": str(result), "error": f"Unexpected type {type(result)}"}
