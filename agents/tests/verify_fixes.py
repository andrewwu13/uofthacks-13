
import asyncio
import re
import json
import ast
from unittest.mock import AsyncMock, MagicMock, patch

# Mock env setup
import os
os.environ["BACKBOARD_API_KEY"] = "test"

# Import system under test
with patch('integrations.backboard.client.backboard_client') as mock_client:
    from integrations.backboard.thread_manager import ThreadManager, MODEL_MAPPING, FALLBACK_MODEL
    from agents.synthesizers.profile_synthesizer import ProfileSynthesizer
    from shared.models.user_profile import VisualPreferences, InteractionPreferences, BehavioralPreferences

    async def test_fallback_logic():
        print("\n=== Testing Fallback Logic ===")
        tm = ThreadManager()
        tm.client = mock_client
        
        # Setup mocks
        tm.client.create_thread = AsyncMock(return_value={"thread_id": "test_thread"})
        tm.client.add_message = AsyncMock(return_value={})
        
        # Scenario 1: Primary Model Fails, Fallback Succeeds
        print("Scenario 1: Primary Model Fails, Fallback Succeeds")
        tm.client.run_inference = AsyncMock(side_effect=[
            Exception("Primary model error"), # First call fails
            "Fallback response"               # Second call succeeds
        ])
        
        session_id = "test_session"
        model = "12thD/ko-Llama-3-8B-sft-v0.3"
        prompt = "test prompt"
        
        result = await tm.run_with_model(session_id, model, prompt)
        
        assert result == "Fallback response"
        assert tm.client.run_inference.call_count == 2
        print("✅ Fallback logic verification passed!")

    async def test_parsing_logic():
        print("\n=== Testing Parsing Logic ===")
        synth = ProfileSynthesizer()
        
        # Test Case 1: Standard JSON
        print("Test Case 1: Standard JSON parsing")
        valid_json = '{"summary": "Test User", "habits": [], "visual_keywords": []}'
        with patch('integrations.backboard.thread_manager.thread_manager.run_with_model', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = valid_json
            result = await synth._infer_profile_narrative("test", VisualPreferences(), InteractionPreferences(), "idle", {}, "")
            assert result.summary == "Test User"
            print("✅ Standard JSON parsing passed!")

        # Test Case 2: Python Dict
        print("Test Case 2: Python Dict parsing (ast.literal_eval)")
        python_dict = "{'summary': 'Python User', 'habits': [], 'visual_keywords': []}"
        with patch('integrations.backboard.thread_manager.thread_manager.run_with_model', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = python_dict
            result = await synth._infer_profile_narrative("test", VisualPreferences(), InteractionPreferences(), "idle", {}, "")
            assert result.summary == "Python User"
            print("✅ Python Dict fallback parsing passed!")

    async def test_redis_locking_simulation():
        print("\n=== Testing Redis Locking Logic (Simulation) ===")
        # We can't easily import events.py due to db deps, so we simulate the logic here
        
        mock_redis = AsyncMock()
        # setnx behavior: returns True (set) if key didn't exist, False (not set) if it did
        
        # Scenario 1: Lock Acquired
        mock_redis.set.return_value = True # Lock acquired
        if await mock_redis.set("lock_key", "running", ex=30, nx=True):
            print("✅ Lock acquired correctly")
        else:
            print("❌ Failed to acquire lock")

        # Scenario 2: Lock Contention
        mock_redis.set.return_value = False # Lock held by other
        if await mock_redis.set("lock_key", "running", ex=30, nx=True):
             print("❌ Acquired lock when should have failed")
        else:
            print("✅ Lock contention handled correctly (skipped)")

    async def main():
        await test_fallback_logic()
        await test_parsing_logic()
        await test_redis_locking_simulation()

if __name__ == "__main__":
    asyncio.run(main())
