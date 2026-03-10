import asyncio
import sys
import os
import datetime
import random
import pytest

# Add project root and backend to path
# __file__ is backend/tests/e2e_persona_vibe_test.py
# parent is backend/tests
# grandparent is backend
# great-grandparent is project root
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root)
sys.path.insert(0, os.path.join(root, "backend"))
sys.path.insert(0, os.path.join(root, "common"))
sys.path.insert(0, os.path.join(root, "backend", "app"))

from agents.graph import run_layout_generation
from app.db.mongo_client import mongo_client
from app.vector.profile_vectors import get_recommended_template_id_async
from app.vector.module_vectors import get_module_by_id

async def seed_historical_data(session_id: str):
    """Seed history snapshots to simulate long-term preference for glassmorphism/minimalism"""
    collection = mongo_client.db.reducer_snapshots
    
    # 1. Previous success with Glassmorphism
    snapshot_1 = {
        "session_id": session_id,
        "timestamp": datetime.datetime.now() - datetime.timedelta(minutes=10),
        "constraints_summary": {
            "hard": {"genre_weights": {"glassmorphism": 0.8, "base": 0.2}},
            "vibe": "Ethereal frosted glass, soft pastel gradients, modern floating UI."
        },
        "behavioral_summary": "High engagement, 45s dwell time on featured glass cards."
    }
    
    # 2. Previous moderate success with Minimalism
    snapshot_2 = {
        "session_id": session_id,
        "timestamp": datetime.datetime.now() - datetime.timedelta(minutes=5),
        "constraints_summary": {
            "hard": {"genre_weights": {"minimalist": 0.7, "base": 0.3}},
            "vibe": "Stark luxury, high whitespace, thin typography."
        },
        "behavioral_summary": "Steady scrolling, focused but less interactive than glassmorphism."
    }
    
    await collection.insert_many([snapshot_1, snapshot_2])
    print(f"Seeded 2 historical snapshots for session: {session_id}")

def generate_organic_telemetry():
    """Simulate a user hovering slowly over a specific element (glassmorphism/minimalist)"""
    telemetry = []
    # Start at top left
    x, y = 50, 50
    # Move towards center where a 'bright' module might be
    tx, ty = 400, 300
    
    for i in range(20):
        # Organic jittery but determined movement towards bright element
        x += (tx - x) * 0.1 + random.uniform(-2, 2)
        y += (ty - y) * 0.1 + random.uniform(-2, 2)
        telemetry.append({
            "x": x, "y": y,
            "velocity": {"x": (tx-x)*0.05, "y": (ty-y)*0.05},
            "acceleration": {"x": 0.1, "y": 0.1},
            "timestamp": i * 50
        })
    
    # Dwelling phase (organic micro-tremors)
    for i in range(21, 50):
        x += random.uniform(-0.5, 0.5)
        y += random.uniform(-0.5, 0.5)
        telemetry.append({
            "x": x, "y": y,
            "velocity": {"x": 0, "y": 0},
            "acceleration": {"x": 0, "y": 0},
            "timestamp": i * 50
        })
    
    return telemetry

@pytest.mark.asyncio
@pytest.mark.integration
async def test_persona_e2e():
    # Ensure MongoDB is connected
    await mongo_client.connect()
    
    session_id = f"persona-bright-minimalist-{random.randint(1000, 9999)}"
    print(f"=== STARTING E2E PERSONA TEST: {session_id} ===")
    print("Target: Bright Colors (Glassmorphism/Vibrant) + Minimalist Secondary")

    # 1. Seed History
    await seed_historical_data(session_id)

    # 2. Prepare Mock Data
    telemetry = generate_organic_telemetry()
    interactions = [
        {"type": "hover", "target_id": "product_glassmorphism_hero", "duration": 5000, "timestamp": 1000},
        {"type": "click", "target_id": "minimalist_filter_btn", "timestamp": 6000}
    ]

    # 3. Run Reworked Pipeline
    print("\n[Step 1] Running Reworked Agent Orchestration...")
    result = await run_layout_generation(
        session_id=session_id,
        telemetry_batch=telemetry,
        interactions=interactions
    )
    
    vibe_summary = result.get("vibe_summary", "")
    print(f"\n@@@RESULT@@@VIBE_SUMMARY: {vibe_summary}")
    print(f"@@@RESULT@@@DESCRIPTION: {result.get('behavioral_description')}")

    # 4. Compare with Vector Store
    print("\n[Step 2] Querying Vector Store for matches...")
    # NOTE: In production code, we'd need to ensure the module vectors are loaded
    from app.vector.vector_store import initialize_vector_store_async
    await initialize_vector_store_async()
    
    template_id, is_explore = await get_recommended_template_id_async(vibe_summary)
    matched_module = get_module_by_id(template_id)

    print(f"\n[Result] Top Recommended Module:")
    if matched_module:
        print(f"- ID: {matched_module.module_id}")
        print(f"- Genre: {matched_module.genre}")
        print(f"- Layout: {matched_module.layout}")
        print(f"- Description: {matched_module.description}")
        
        # Check alignment
        is_aligned = matched_module.genre in ["glassmorphism", "minimalist", "loud"]
        print(f"\n[Alignment Check] {'SUCCESS' if is_aligned else 'FAILURE'}")
        print(f"Goal was Bright (Glass/Vibrant) or Minimalist. Matched: {matched_module.genre}")
        
        # Assert for pytest
        assert is_aligned, f"Expected genre to be in [glassmorphism, minimalist, loud], got {matched_module.genre}"
    else:
        print("- [Error] No module matched.")
        pytest.fail("No module matched in vector store.")
