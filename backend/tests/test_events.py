from fastapi.testclient import TestClient
from app.main import app
import logging

# Mute logging during tests to keep output clean
logging.getLogger("uvicorn").setLevel(logging.WARNING)

client = TestClient(app)

def test_telemetry_payload_structure():
    """
    Test payload matching the exact structure requested by user.
    Verifies that the backend accepts the data and returns 200 OK.
    """
    payload = {
      "session_id": "session_test_123",
      "device_type": "desktop",
      "timestamp": 1737138008,
      "events": [
        {
          "ts": 1737138006,
          "type": "click_rage",
          "target_id": "submit_btn",
          "position": { "x": 500, "y": 300 },
          "metadata": { 
            "click_count": 5, 
            "duration_ms": 800 
          }
        },
        {
            "ts": 1737138007,
            "type": "hover",
            "target_id": "product_card_1",
            "duration_ms": 450,
            "metadata": { "track_context": "price" }
        }
      ],
      "motor": {
        "session_id": "session_test_123",
        "device": "mouse",
        "t0": 1737138005,
        "dt": 16,
        "samples": [
          [100, 200], [105, 202], [110, 205]
        ]
      }
    }
    
    response = client.post("/telemetry/events", json=payload)
    
    # Check successful response
    assert response.status_code == 200
    print(f"DEBUG RESPONSE: {response.json()}")

    # Verify response structure
    
    # Verify response structure
    data = response.json()
    assert data["session_id"] == "session_test_123"
    assert data["received"] == 2
    assert data["status"] == "ok"

def test_telemetry_payload_minimal():
    """Test minimal payload without motor data"""
    payload = {
      "session_id": "session_min_456",
      "device_type": "mobile",
      "timestamp": 1737139000,
      "events": [
        {
          "ts": 1737139000,
          "type": "visibility_change",
          "target_id": "document"
        }
      ]
    }
    
    response = client.post("/telemetry/events", json=payload)
    assert response.status_code == 200
    assert response.json()["received"] == 1
