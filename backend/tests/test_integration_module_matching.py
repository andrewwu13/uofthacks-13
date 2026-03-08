
import pytest
import asyncio
from app.vector.vector_store import initialize_vector_store_async, search_similar_modules
from app.vector.profile_vectors import user_profile_to_vector_async
from app.vector.module_vectors import decode_module_id, get_module_by_id
from app.config import settings

@pytest.mark.integration
@pytest.mark.asyncio
async def test_module_matching_live():
    """Live integration test for OpenRouter module matching."""
    if not settings.OPENROUTER_API_KEY or settings.OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        pytest.skip("OPENROUTER_API_KEY not set")

    # 1. Initialize Vector Store
    await initialize_vector_store_async()
    
    # 2. Define a mock user description
    mock_summary = "A high-tech enthusiast who prefers dark terminal-like interfaces, green phosphor glow, and dense tactical information displays."
    
    mock_profile = {
        "vibe_summary": mock_summary
    }
    
    # 3. Generate the user profile vector
    profile_vector = await user_profile_to_vector_async(mock_profile)
    
    # 4. Search for similar modules
    results = search_similar_modules(profile_vector, top_k=5)
    recommendations = results.get("recommended", [])
    
    assert len(recommendations) > 0
    
    # Top match should be cyber
    top_match = recommendations[0]
    decoded = decode_module_id(top_match.id)
    
    assert decoded["genre"] == "cyber"
    assert top_match.score > 0.5
