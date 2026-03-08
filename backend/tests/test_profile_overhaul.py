import os
import sys

# Standardize path for root imports
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
common_path = os.path.join(root_path, "common")
if common_path not in sys.path:
    sys.path.append(common_path)
if root_path not in sys.path:
    sys.path.append(root_path)

import pytest
import asyncio
import hashlib
from unittest.mock import AsyncMock, patch
from agents.synthesizers.profile_synthesizer import profile_synthesizer
from backend.app.vector.profile_vectors import user_profile_to_vector_async
from backend.app.services.cache_service import cache_service
from shared.models.user_profile import UserProfile

@pytest.mark.asyncio
async def test_synthesis_logic_vibe_summary():
    """Verify that the synthesizer produces a string summary with 80/20 logic."""
    mock_stability = {"add_modules": [{"genre": "minimalist"}]}
    mock_exploratory = {"add_modules": [{"genre": "loud"}]}
    
    with patch("integrations.backboard.thread_manager.thread_manager.run_with_model", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "A minimalist user (80%) with a slight interest in loud patterns (20%)."
        
        result = await profile_synthesizer.synthesize(
            session_id="test_session",
            stability_proposal=mock_stability,
            exploratory_proposal=mock_exploratory,
            motor_state="browsing",
            motor_confidence=0.9,
            context_analysis={"insights": "User likes whitespace."}
        )
        
        assert isinstance(result['vibe_summary'], str)
        assert "minimalist" in result['vibe_summary'].lower()

@pytest.mark.asyncio
async def test_profile_vector_exact_match_cache():
    """Verify that redundant vibe summaries use the Redis cache."""
    test_summary = "Unique Test Summary for Cache"
    mock_profile = {"vibe_summary": test_summary}
    
    # Mock Redis get/set via the cache_service instance
    cache_store = {}
    async def mock_set(key, val, ttl=0): cache_store[key] = val
    async def mock_get(key): return cache_store.get(key)
    
    # Mock Redis get/set via the specific instance used in profile_vectors
    cache_store = {}
    async def mock_set(key, val, ttl=0): cache_store[key] = val
    async def mock_get(key): return cache_store.get(key)
    
    with patch("app.vector.profile_vectors.cache_service.get", side_effect=mock_get) as mock_get_call, \
         patch("app.vector.profile_vectors.cache_service.set", side_effect=mock_set) as mock_set_call, \
         patch("langchain_openai.OpenAIEmbeddings.embed_query", return_value=[0.1]*1536) as mock_embed:
        
        # First call (Should trigger embedding)
        await user_profile_to_vector_async(mock_profile)
        print(f"DEBUG: Cache Store after first call: {cache_store.keys()}")
        assert mock_embed.call_count == 1
        
        # Second call (Should retrieve from cache_store)
        await user_profile_to_vector_async(mock_profile)
        print(f"DEBUG: Mock GET call count: {mock_get_call.call_count}")
        # Still should be 1 call total because hit cache
        assert mock_embed.call_count == 1

@pytest.mark.asyncio
async def test_schema_vibe_summary_existence():
    """Verify UserProfile schema has the correct field."""
    p = UserProfile(vibe_summary="Test")
    data = p.model_dump()
    assert "vibe_summary" in data
    assert data["vibe_summary"] == "Test"
