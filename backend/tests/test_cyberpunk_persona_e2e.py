"""
E2E Classification Test: Cyberpunk Persona
==========================================
Mocks telemetry data that EXACTLY matches the frontend payload structure
(see frontend/src/tracking/types.ts) for a user who prefers the Cyberpunk look.

The simulated user:
  - Scrolls quickly through glassmorphism and minimalist modules (passing over, low dwell)
  - Slows down and dwells on cyberpunk modules
  - Clicks on the cyberpunk hero and cyberpunk CTA modules
  - Shows one "rage click" on the minimalist section (frustration signal)
  - Has medium exploration tolerance (interacts with one loud/test module)

Goal: Assert the system recommends a cyberpunk genre module.
"""

import asyncio
import sys
import os
import math
import random
import datetime
import pytest

# --- Path Setup ---
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root)
sys.path.insert(0, os.path.join(root, "backend"))
sys.path.insert(0, os.path.join(root, "common"))
sys.path.insert(0, os.path.join(root, "backend", "app"))

from agents.graph import run_layout_generation
from app.db.mongo_client import mongo_client
from app.vector.profile_vectors import get_recommended_template_id_async
from app.vector.module_vectors import get_module_by_id, GENRE_MAP


# ===========================================================
# MOCK DATA GENERATION
# Matches frontend types exactly:
#   MotorTelemetryPayload.samples: [[x, y], ...]
#   TelemetryEvent: { ts, type, target_id, duration_ms?, position?, metadata? }
# ===========================================================

def generate_cyberpunk_motor_samples() -> list[list[float]]:
    """
    Generate motor samples as [[x, y], ...] arrays, exactly matching the
    frontend MotorTelemetryPayload.samples format.

    Simulates a user:
    1. Fast, determined scroll through the top (glassmorphism hero) - high velocity
    2. Slowing down around the cyberpunk section - decreasing velocity
    3. Dwelling motionless over the cyberpunk hero - near-zero velocity (dwell)
    4. A quick click burst on the cyberpunk hero - sharp impulse
    5. More browsing through the bottom of page
    """
    samples = []
    x, y = 640.0, 80.0  # Start near the top center

    # Phase 1: Fast scroll past glassmorphism (high velocity, linear)
    # ~40 samples at 16ms each = 640ms of fast movement
    for i in range(40):
        x += random.uniform(-5, 5)   # slight horizontal jitter
        y += 18 + random.uniform(-2, 2)  # fast downward scroll
        samples.append([round(x, 2), round(y, 2)])

    # Phase 2: Neon section approaching - deceleration into cyberpunk area
    # ~20 samples slowing from fast to stop
    vy = 18.0
    for i in range(20):
        vy *= 0.85  # decelerate
        x += random.uniform(-2, 2)
        y += vy + random.uniform(-1, 1)
        samples.append([round(x, 2), round(y, 2)])

    # Phase 3: DWELL on cyberpunk module - micro-tremors only
    # ~60 samples of near-zero movement → low velocity = high interest signal
    cx, cy = x, y  # anchor point
    for i in range(60):
        # Organic micro-tremors: tiny random walk
        x = cx + math.sin(i * 0.3) * 1.2 + random.uniform(-0.5, 0.5)
        y = cy + math.cos(i * 0.2) * 0.8 + random.uniform(-0.5, 0.5)
        samples.append([round(x, 2), round(y, 2)])

    # Phase 4: Sharp click impulse (rapid movement to button then stop)
    # Sudden pointing movement = determined gesture
    tx, ty = cx + 80, cy + 30  # target: cyberpunk BUY button position
    for i in range(10):
        progress = (i + 1) / 10.0
        x = cx + (tx - cx) * progress + random.uniform(-1, 1)
        y = cy + (ty - cy) * progress + random.uniform(-1, 1)
        samples.append([round(x, 2), round(y, 2)])

    # Phase 5: Post-click drift downward, browsing behavior
    for i in range(30):
        x += random.uniform(-3, 3)
        y += 8 + random.uniform(-3, 3)
        samples.append([round(x, 2), round(y, 2)])

    return samples


def generate_cyberpunk_events(t_base: int) -> list[dict]:
    """
    Generate interaction events matching the frontend TelemetryEvent format:
      { ts, type, target_id, duration_ms?, position?, metadata? }

    Module metadata fields match exactly what InteractionTracker.getElementMetadata() produces:
      - module_genre: the CSS genre class extracted from DOM
      - module_type (bento layout type)
      - is_loud: whether it's an A/B exploration module
      - tag_name, class_name, track_context
    """
    events = []

    # --- 1. Enter viewport: glassmorphism hero (quick pass) ---
    events.append({
        "ts": t_base + 200,
        "type": "enter_viewport",
        "target_id": "glassmorphism-hero-1",
        "position": {"x": 640, "y": 120},
        "metadata": {
            "module_genre": "glassmorphism",
            "module_type": "hero",
            "is_loud": False,
            "tag_name": "div",
            "class_name": "bento-item bento-hero genre-glassmorphism",
            "track_context": None,
        }
    })

    # --- 2. Brief hover-enter glassmorphism (below threshold → NOT engaging) ---
    events.append({
        "ts": t_base + 300,
        "type": "hover-enter",
        "target_id": "glassmorphism-hero-1",
        "position": {"x": 640, "y": 200},
        "metadata": {
            "module_genre": "glassmorphism",
            "module_type": "hero",
            "is_loud": False,
            "tag_name": "div",
            "class_name": "bento-item bento-hero genre-glassmorphism",
            "track_context": None,
        }
    })

    # Quick departure from glassmorphism (only 150ms dwell = below threshold)
    events.append({
        "ts": t_base + 450,
        "type": "hover-leave",
        "target_id": "glassmorphism-hero-1",
        "duration_ms": 150,
        "position": {"x": 640, "y": 200},
        "metadata": {
            "module_genre": "glassmorphism",
            "module_type": "hero",
            "is_loud": False,
            "tag_name": "div",
            "class_name": "bento-item bento-hero genre-glassmorphism",
            "track_context": None,
        }
    })

    # --- 3. Scroll stop above minimalist section (no engagement) ---
    events.append({
        "ts": t_base + 900,
        "type": "scroll_stop",
        "target_id": "page",
        "position": {"x": 640, "y": 520},
        "metadata": {
            "module_genre": None,
            "module_type": None,
            "is_loud": False,
            "tag_name": "body",
            "class_name": "",
            "track_context": None,
        }
    })

    # --- 4. Rage click on minimalist section (frustration signal) ---
    events.append({
        "ts": t_base + 1100,
        "type": "click_rage",
        "target_id": "minimalist-wide-1",
        "position": {"x": 540, "y": 560},
        "metadata": {
            "module_genre": "minimalist",
            "module_type": "wide",
            "is_loud": False,
            "tag_name": "div",
            "class_name": "bento-item bento-wide genre-minimalist",
            "track_context": None,
        }
    })

    # --- 5. Enter cyberpunk hero section ---
    events.append({
        "ts": t_base + 1500,
        "type": "enter_viewport",
        "target_id": "cyberpunk-hero-1",
        "position": {"x": 640, "y": 820},
        "metadata": {
            "module_genre": "cyberpunk",
            "module_type": "hero",
            "is_loud": False,
            "tag_name": "div",
            "class_name": "bento-item bento-hero genre-cyberpunk",
            "track_context": None,
        }
    })

    # --- 6. Significant hover on cyberpunk hero (4800ms = strong engagement) ---
    events.append({
        "ts": t_base + 1600,
        "type": "hover-enter",
        "target_id": "cyberpunk-hero-1",
        "position": {"x": 660, "y": 880},
        "metadata": {
            "module_genre": "cyberpunk",
            "module_type": "hero",
            "is_loud": False,
            "tag_name": "div",
            "class_name": "bento-item bento-hero genre-cyberpunk",
            "track_context": None,
        }
    })

    events.append({
        "ts": t_base + 6400,
        "type": "hover",  # Significant hover event (emitted on leave if > threshold)
        "target_id": "cyberpunk-hero-1",
        "duration_ms": 4800,
        "position": {"x": 660, "y": 880},
        "metadata": {
            "module_genre": "cyberpunk",
            "module_type": "hero",
            "is_loud": False,
            "tag_name": "div",
            "class_name": "bento-item bento-hero genre-cyberpunk",
            "track_context": None,
        }
    })

    # --- 7. Click on cyberpunk hero buy button ---
    events.append({
        "ts": t_base + 6600,
        "type": "click",
        "target_id": "cyberpunk-hero-1",
        "position": {"x": 720, "y": 910},
        "metadata": {
            "module_genre": "cyberpunk",
            "module_type": "hero",
            "is_loud": False,
            "tag_name": "div",
            "class_name": "bento-item bento-hero genre-cyberpunk",
            "track_context": "buy_button",
        }
    })

    # --- 8. Hover on cyberpunk tall module (secondary positive signal) ---
    events.append({
        "ts": t_base + 7200,
        "type": "hover-enter",
        "target_id": "cyberpunk-tall-1",
        "position": {"x": 900, "y": 920},
        "metadata": {
            "module_genre": "cyberpunk",
            "module_type": "tall",
            "is_loud": False,
            "tag_name": "div",
            "class_name": "bento-item bento-tall genre-cyberpunk",
            "track_context": None,
        }
    })

    events.append({
        "ts": t_base + 9400,
        "type": "hover",
        "target_id": "cyberpunk-tall-1",
        "duration_ms": 2200,
        "position": {"x": 900, "y": 920},
        "metadata": {
            "module_genre": "cyberpunk",
            "module_type": "tall",
            "is_loud": False,
            "tag_name": "div",
            "class_name": "bento-item bento-tall genre-cyberpunk",
            "track_context": None,
        }
    })

    # --- 9. Click on a "loud" (exploration) monoprint module ---
    # Signals medium exploration tolerance (open to similar dark aesthetics)
    events.append({
        "ts": t_base + 10000,
        "type": "click",
        "target_id": "monoprint-wide-loud-1",
        "position": {"x": 400, "y": 1100},
        "metadata": {
            "module_genre": "monoprint",
            "module_type": "wide",
            "is_loud": True,  # This is an A/B exploration module
            "tag_name": "div",
            "class_name": "bento-item bento-wide genre-monoprint",
            "track_context": "exploration_module",
        }
    })

    # --- 10. Hover over cyberpunk small product card (further reinforcement) ---
    events.append({
        "ts": t_base + 10500,
        "type": "hover",
        "target_id": "cyberpunk-small-1",
        "duration_ms": 1100,
        "position": {"x": 300, "y": 1200},
        "metadata": {
            "module_genre": "cyberpunk",
            "module_type": "small",
            "is_loud": False,
            "tag_name": "div",
            "class_name": "bento-item bento-small genre-cyberpunk",
            "track_context": None,
        }
    })

    return events


async def seed_neutral_history(session_id: str) -> bool:
    """
    Seed a neutral prior session (no strong genre preference).
    Returns True if seeding succeeded, False if MongoDB is unavailable.
    """
    try:
        await mongo_client.connect(max_retries=1, retry_delay=0.5)
        collection = mongo_client.db.reducer_snapshots
        await collection.insert_many([
            {
                "session_id": session_id,
                "timestamp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=15),
                "vibe_summary": "New user, no established preference. Standard clean layout.",
                "constraints_summary": {
                    "hard": {"genre_weights": {"glassmorphism": 0.2, "minimalist": 0.2, "cyberpunk": 0.2, "brutalism": 0.2}},
                    "vibe": "New user"
                },
                "behavioral_summary": "First session, no significant interactions recorded.",
                "suggested_id": 0
            }
        ])
        print(f"[Seed] Seeded 1 neutral history snapshot for session: {session_id}")
        return True
    except Exception as e:
        print(f"[Seed] WARNING: MongoDB unavailable ({e}). Skipping history seed — "
              "long context agent will see empty history. Test continues.")
        return False


# ===========================================================
# PYTEST TEST
# ===========================================================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_cyberpunk_persona_e2e():
    """
    Full E2E test for a cyberpunk-preferring user.

    Mock data exactly matches frontend TelemetryBatch payload:
    - motor.samples: [[x, y], ...] (MotorTelemetryPayload format)
    - events: List[TelemetryEvent] with metadata matching InteractionTracker output
    
    Expected Result: Recommended module genre = 'cyberpunk'
    """
    print("\n" + "="*60)
    print("E2E PERSONA TEST: CYBERPUNK USER")
    print("="*60)

    session_id = f"e2e-cyberpunk-{random.randint(10000, 99999)}"
    t_base = 1741538000  # Unix timestamp base

    print(f"Session ID: {session_id}")
    print(f"Target Persona: Cyberpunk (dark, neon, scanline, terminal aesthetic)")

    # 1. Seed neutral prior history
    await seed_neutral_history(session_id)

    # 2. Generate mocked motor data (frontend-format [[x, y], ...] samples)
    raw_samples = generate_cyberpunk_motor_samples()
    motor_dt = 16  # 16ms between samples (60fps)
    motor_t0 = t_base * 1000  # milliseconds

    # Transform to the format expected by transform_motor_samples() in events.py
    # (MotorTelemetryPayload → processed list with velocity/acceleration dicts)
    from app.api.events import transform_motor_samples
    from app.models.events import MotorTelemetryPayload

    motor_payload = MotorTelemetryPayload(
        session_id=session_id,
        device="mouse",
        t0=float(motor_t0),
        dt=float(motor_dt),
        samples=raw_samples
    )
    processed_motor = transform_motor_samples(motor_payload)
    print(f"Generated {len(raw_samples)} motor samples → {len(processed_motor)} processed datapoints")

    # 3. Generate mocked interaction events (frontend TelemetryEvent format)
    interaction_events = generate_cyberpunk_events(t_base)
    print(f"Generated {len(interaction_events)} interaction events")

    # Print event summary
    from collections import Counter
    event_types = Counter(e["type"] for e in interaction_events)
    genres_touched = Counter(
        e["metadata"].get("module_genre")
        for e in interaction_events
        if e.get("metadata") and e["metadata"].get("module_genre")
    )
    print(f"\nEvent type distribution: {dict(event_types)}")
    print(f"Genres interacted with: {dict(genres_touched)}")
    print(f"Loud module events: {sum(1 for e in interaction_events if (e.get('metadata') or {}).get('is_loud'))}")

    # 4. Filter loud events (matching events.py logic)
    loud_events = [
        e for e in interaction_events
        if (e.get("metadata") or {}).get("is_loud", False)
        or "loud" in (e.get("target_id") or "").lower()
    ]
    print(f"Loud events detected: {len(loud_events)}")

    # 5. Run Agent Ensemble
    print("\n[Step 1] Running LangGraph Agent Ensemble...")
    result = await run_layout_generation(
        session_id=session_id,
        telemetry_batch=processed_motor,
        interactions=interaction_events,
        loud_module_events=loud_events,
        current_preferences={}
    )

    vibe_summary = result.get("vibe_summary", "")
    behavioral_desc = result.get("behavioral_description", "")

    print(f"\n--- AGENT RESULTS ---")
    print(f"Behavioral Description: {behavioral_desc}")
    print(f"Vibe Summary: {vibe_summary}")

    assert vibe_summary, "Agent ensemble should return a non-empty vibe summary"

    # 6. Vector Store Matching
    print("\n[Step 2] Querying Vector Store for best matching module...")
    from app.vector.vector_store import initialize_vector_store_async
    await initialize_vector_store_async()

    template_id, is_explore = await get_recommended_template_id_async(vibe_summary)
    matched_module = get_module_by_id(template_id)

    print(f"\n--- VECTOR STORE RESULT ---")
    if matched_module:
        print(f"Recommended Module ID : {matched_module.module_id}")
        print(f"Recommended Genre     : {matched_module.genre}")
        print(f"Recommended Layout    : {matched_module.layout}")
        print(f"Recommendation Type   : {'🔍 EXPLORE' if is_explore else '🎯 EXPLOIT'}")
        print(f"Description Snippet   : {matched_module.description[:100]}...")

        # 7. Alignment Check
        # Primary target: cyberpunk
        # Acceptable secondary: monoprint (shares dark aesthetic)
        ACCEPTABLE_GENRES = {"cyberpunk", "monoprint"}
        is_aligned = matched_module.genre in ACCEPTABLE_GENRES

        print(f"\n{'='*60}")
        print(f"CLASSIFICATION: {'✅ SUCCESS' if is_aligned else '❌ FAILURE'}")
        print(f"Expected genres: {ACCEPTABLE_GENRES}")
        print(f"Got genre: {matched_module.genre}")
        print(f"{'='*60}\n")

        assert is_aligned, (
            f"Expected cyberpunk or monoprint (dark, neon aesthetic). "
            f"Got '{matched_module.genre}' (ID={template_id}).\n"
            f"Vibe Summary was: '{vibe_summary}'"
        )
    else:
        pytest.fail(f"Vector store returned no matched module for template_id={template_id}")
