
import pytest
import httpx
import json

SAMPLE_PAYLOAD = {
    "session_id": "session_test_telemetry_integration",
    "device_type": "desktop",
    "timestamp": 1737138008,
    "events": [
        {
            "ts": 1737138006,
            "type": "click_rage",
            "target_id": "submit_btn",
            "position": {"x": 500, "y": 300},
            "metadata": {"click_count": 5, "duration_ms": 800},
        }
    ],
    "motor": {
        "session_id": "session_test_telemetry_integration",
        "device": "mouse",
        "t0": 1737138005,
        "dt": 16,
        "samples": [[100, 200], [105, 202]],
    },
}

@pytest.mark.integration
@pytest.mark.asyncio
async def test_telemetry_endpoint_live():
    """Integration test for telemetry endpoint (requires running server)."""
    url = "http://localhost:8000/telemetry/events"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=SAMPLE_PAYLOAD, timeout=2.0)
            assert response.status_code == 200
            assert response.json()["status"] == "success"
        except (httpx.ConnectError, httpx.TimeoutException):
            pytest.skip("Server is not running on localhost:8000")
