#!/usr/bin/env python3
"""
Test script to print and optionally send the telemetry payload structure.
Run: python3 scripts/test_telemetry_payload.py
"""
import json

# Complete payload structure matching frontend → backend contract
SAMPLE_PAYLOAD = {
    "session_id": "session_1737138005123_abc123",
    "device_type": "desktop",  # "desktop" | "mobile" | "tablet"
    "timestamp": 1737138008,
    "events": [
        {
            "ts": 1737138006,
            "type": "click_rage",
            "target_id": "submit_btn",
            "position": {"x": 500, "y": 300},
            "duration_ms": None,
            "metadata": {
                "click_count": 5,
                "duration_ms": 800
            }
        },
        {
            "ts": 1737138007,
            "type": "hover",
            "target_id": "product_card_1",
            "position": {"x": 200, "y": 400},
            "duration_ms": 450,
            "metadata": {"track_context": "price"}
        },
        {
            "ts": 1737138007,
            "type": "dead_click",
            "target_id": "fake_button",
            "position": {"x": 300, "y": 500},
            "metadata": {"text": "Fake Button", "cursor": "pointer"}
        },
        {
            "ts": 1737138008,
            "type": "click_error",
            "target_id": "error_btn",
            "position": {"x": 400, "y": 600},
            "metadata": {"error": "Simulated Click Error!"}
        }
    ],
    "motor": {
        "session_id": "session_1737138005123_abc123",
        "device": "mouse",  # "mouse" | "touch"
        "t0": 1737138005,
        "dt": 16,  # milliseconds between samples
        "samples": [
            [100, 200],
            [105, 202],
            [110, 205],
            [118, 210],
            [125, 218]
        ]
    }
}

def main():
    print("=" * 60)
    print("TELEMETRY PAYLOAD STRUCTURE")
    print("Endpoint: POST /telemetry/events")
    print("=" * 60)
    print()
    print(json.dumps(SAMPLE_PAYLOAD, indent=2))
    print()
    print("=" * 60)
    
    # Optional: Send to running server
    try:
        import httpx
        response = httpx.post(
            "http://localhost:8000/telemetry/events",
            json=SAMPLE_PAYLOAD,
            timeout=5.0
        )
        print(f"\nSent to server! Response: {response.json()}")
    except Exception as e:
        print(f"\n(Server not running or unreachable: {e})")

if __name__ == "__main__":
    main()
