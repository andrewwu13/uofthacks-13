"""
Agent Workflow Test Script - Live API Integration
Tests the full agent pipeline with 3 mock user personas using REAL Backboard API calls.
"""
import asyncio
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.graph import run_layout_generation


# =============================================================================
# MOCK DATA GENERATORS (Correct telemetry format)
# =============================================================================

def generate_confident_contrasty_user():
    """
    User 1: Confident shopper, prefers high-contrast/dark designs
    - Smooth, linear mouse movements (determined)
    - Quick, decisive hovers
    - Positive engagement with neobrutalist/dark modules
    """
    return {
        "session_id": "test-user-confident-contrasty",
        # Telemetry: velocity and acceleration as {x, y} dicts
        "telemetry_batch": [
            {"x": 100, "y": 200, "timestamp": 1000, "velocity": {"x": 400, "y": 200}, "acceleration": {"x": 15, "y": 10}},
            {"x": 200, "y": 250, "timestamp": 1100, "velocity": {"x": 420, "y": 210}, "acceleration": {"x": 12, "y": 8}},
            {"x": 350, "y": 300, "timestamp": 1200, "velocity": {"x": 450, "y": 180}, "acceleration": {"x": 10, "y": 5}},
            {"x": 500, "y": 320, "timestamp": 1300, "velocity": {"x": 480, "y": 150}, "acceleration": {"x": 8, "y": 3}},
            {"x": 650, "y": 350, "timestamp": 1400, "velocity": {"x": 500, "y": 120}, "acceleration": {"x": 5, "y": 2}},
        ],
        "interactions": [
            {"type": "hover", "element_id": "hero-neobrutalist", "genre": "neobrutalist", "duration_ms": 800},
            {"type": "click", "element_id": "cta-dark", "genre": "neobrutalist", "duration_ms": 100},
            {"type": "hover", "element_id": "grid-dark", "genre": "neobrutalist", "duration_ms": 600},
        ],
        "loud_module_events": [
            {"module_id": "loud-neobrutalist-1", "genre": "neobrutalist", "dwell_time_ms": 3500, "scroll_velocity": 100, "clicked": True},
            {"module_id": "loud-minimalist-1", "genre": "minimalist", "dwell_time_ms": 400, "scroll_velocity": 600, "clicked": False},
        ],
        "current_preferences": {
            "genre_weights": {"base": 0.5, "minimalist": 0.3, "neobrutalist": 0.5, "glassmorphism": 0.3}
        },
        "expected": {
            "motor_state": "determined",
            "color_scheme": "dark",
            "decision_confidence": "high",
            "typography_weight": "bold",
        },
    }


def generate_indecisive_pastel_user():
    """
    User 2: Indecisive shopper, prefers soft pastel designs
    - Jittery, hesitant mouse movements (high jerk, direction changes)
    - Long hovers, back-and-forth navigation
    - Positive engagement with minimalist/glassmorphism modules
    """
    return {
        "session_id": "test-user-indecisive-pastel",
        # Telemetry: Jittery movements with direction changes
        "telemetry_batch": [
            {"x": 100, "y": 200, "timestamp": 1000, "velocity": {"x": 50, "y": 30}, "acceleration": {"x": 120, "y": 80}},
            {"x": 105, "y": 195, "timestamp": 1100, "velocity": {"x": -30, "y": -20}, "acceleration": {"x": -100, "y": -70}},
            {"x": 110, "y": 210, "timestamp": 1200, "velocity": {"x": 60, "y": 40}, "acceleration": {"x": 150, "y": 100}},
            {"x": 108, "y": 205, "timestamp": 1300, "velocity": {"x": -20, "y": -15}, "acceleration": {"x": -80, "y": -60}},
            {"x": 115, "y": 215, "timestamp": 1400, "velocity": {"x": 45, "y": 35}, "acceleration": {"x": 110, "y": 90}},
        ],
        "interactions": [
            {"type": "hover", "element_id": "hero-minimalist", "genre": "minimalist", "duration_ms": 4500},
            {"type": "hover", "element_id": "grid-glassmorphism", "genre": "glassmorphism", "duration_ms": 3800},
            {"type": "scroll", "direction": "up", "velocity": 100, "duration_ms": 800},
            {"type": "hover", "element_id": "hero-minimalist", "genre": "minimalist", "duration_ms": 2500},
        ],
        "loud_module_events": [
            {"module_id": "loud-glassmorphism-1", "genre": "glassmorphism", "dwell_time_ms": 5000, "scroll_velocity": 50, "clicked": True},
            {"module_id": "loud-neobrutalist-1", "genre": "neobrutalist", "dwell_time_ms": 200, "scroll_velocity": 800, "clicked": False},
        ],
        "current_preferences": {
            "genre_weights": {"base": 0.5, "minimalist": 0.4, "neobrutalist": 0.2, "glassmorphism": 0.4}
        },
        "expected": {
            "motor_state": "anxious",
            "color_scheme": "light",
            "decision_confidence": "low",
            "typography_weight": "light",
            "density": "low",
        },
    }


def generate_indecisive_brutalist_user():
    """
    User 3: Indecisive shopper, prefers brutalist designs
    - Jittery movements but drawn to bold elements
    - Long hovers on neobrutalist modules despite hesitation
    """
    return {
        "session_id": "test-user-indecisive-brutalist",
        # Telemetry: Jittery but drawn to bold
        "telemetry_batch": [
            {"x": 200, "y": 300, "timestamp": 1000, "velocity": {"x": 80, "y": 60}, "acceleration": {"x": 180, "y": 120}},
            {"x": 210, "y": 290, "timestamp": 1100, "velocity": {"x": -50, "y": -40}, "acceleration": {"x": -130, "y": -100}},
            {"x": 205, "y": 310, "timestamp": 1200, "velocity": {"x": 70, "y": 55}, "acceleration": {"x": 160, "y": 110}},
            {"x": 220, "y": 295, "timestamp": 1300, "velocity": {"x": -60, "y": -45}, "acceleration": {"x": -100, "y": -80}},
            {"x": 215, "y": 320, "timestamp": 1400, "velocity": {"x": 75, "y": 50}, "acceleration": {"x": 140, "y": 95}},
        ],
        "interactions": [
            {"type": "hover", "element_id": "hero-neobrutalist", "genre": "neobrutalist", "duration_ms": 5000},
            {"type": "hover", "element_id": "grid-neobrutalist", "genre": "neobrutalist", "duration_ms": 4200},
            {"type": "scroll", "direction": "up", "velocity": 120, "duration_ms": 500},
            {"type": "hover", "element_id": "hero-neobrutalist", "genre": "neobrutalist", "duration_ms": 3500},
        ],
        "loud_module_events": [
            {"module_id": "loud-neobrutalist-bold", "genre": "neobrutalist", "dwell_time_ms": 6000, "scroll_velocity": 80, "clicked": True},
            {"module_id": "loud-minimalist-soft", "genre": "minimalist", "dwell_time_ms": 300, "scroll_velocity": 700, "clicked": False},
        ],
        "current_preferences": {
            "genre_weights": {"base": 0.5, "minimalist": 0.3, "neobrutalist": 0.4, "glassmorphism": 0.3}
        },
        "expected": {
            "motor_state": "anxious",
            "color_scheme": "dark",
            "decision_confidence": "low",
            "typography_weight": "bold",
            "density": "high",
        },
    }


# =============================================================================
# TEST RUNNER (Live API Calls)
# =============================================================================

async def run_single_user_test(user_data: dict) -> dict:
    """Run the agent workflow for a single user with LIVE API calls"""
    print(f"\n{'='*60}")
    print(f"Testing: {user_data['session_id']}")
    print(f"{'='*60}")
    
    try:
        user_profile = await run_layout_generation(
            session_id=user_data["session_id"],
            telemetry_batch=user_data["telemetry_batch"],
            interactions=user_data["interactions"],
            loud_module_events=user_data["loud_module_events"],
            current_preferences=user_data["current_preferences"],
        )
        
        print(f"SUCCESS: Generated User Profile")
        print(json.dumps(user_profile, indent=2))
        
        # Validate against expected traits
        expected = user_data["expected"]
        matches = []
        mismatches = []
        
        for key, expected_val in expected.items():
            if key == "motor_state":
                actual = "N/A (not in final profile)"
                matches.append(f"  [SKIP] {key}: {expected_val} (not in profile)")
                continue
            elif key in ["color_scheme", "corner_radius", "button_size", "density", "typography_weight"]:
                actual = user_profile.get("visual", {}).get(key)
            elif key in ["decision_confidence", "exploration_tolerance", "scroll_behavior"]:
                actual = user_profile.get("interaction", {}).get(key)
            elif key in ["speed_vs_accuracy", "engagement_depth"]:
                actual = user_profile.get("behavioral", {}).get(key)
            else:
                actual = None
            
            if actual == expected_val:
                matches.append(f"  [Y] {key}: {actual}")
            else:
                mismatches.append(f"  [N] {key}: expected={expected_val}, actual={actual}")
        
        print("\nValidation Results:")
        for m in matches:
            print(m)
        for m in mismatches:
            print(m)
        
        return {
            "session_id": user_data["session_id"],
            "success": True,
            "user_profile": user_profile,
            "matches": len(matches),
            "mismatches": len(mismatches),
        }
        
    except Exception as e:
        import traceback
        print(f"FAILED: {e}")
        traceback.print_exc()
        return {
            "session_id": user_data["session_id"],
            "success": False,
            "error": str(e),
        }


async def main():
    """Main test runner"""
    print("\n[*] Starting Agent Workflow Test Suite (LIVE API Calls)")
    print("Testing 3 mock user personas through the full agent pipeline...")
    print("Note: This test makes REAL calls to Backboard.io API\n")
    
    users = [
        generate_confident_contrasty_user(),
        generate_indecisive_pastel_user(),
        generate_indecisive_brutalist_user(),
    ]
    
    results = []
    for user_data in users:
        result = await run_single_user_test(user_data)
        results.append(result)
    
    # Summary
    print("\n" + "="*80)
    print(" SUMMARY")
    print("="*80)
    
    success_count = sum(1 for r in results if r["success"])
    print(f"Tests passed: {success_count}/{len(results)}")
    
    for r in results:
        status = "PASS" if r["success"] else "FAIL"
        print(f"  [{status}] {r['session_id']}")
        if r["success"]:
            print(f"        Matches: {r['matches']}, Mismatches: {r['mismatches']}")
        else:
            print(f"        Error: {r.get('error', 'Unknown')}")
    
    print("="*80)
    return results


if __name__ == "__main__":
    asyncio.run(main())
