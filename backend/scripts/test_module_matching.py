
import asyncio
import os
import sys
from pathlib import Path

# Add backend to sys.path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from app.config import settings
from app.vector.vector_store import VectorStore, initialize_vector_store_async
from app.vector.profile_vectors import user_profile_to_vector_async
from app.vector.module_vectors import decode_module_id

async def test_module_matching():
    # 1. Initialize Vector Store (this computes all module embeddings)
    print("Initializing Vector Store and computing module embeddings...")
    await initialize_vector_store_async()
    
    # 2. Define a mock user description
    # This description is heavily biased towards the 'cyber' aesthetic
    mock_summary = "A high-tech enthusiast who prefers dark terminal-like interfaces, green phosphor glow, and dense tactical information displays."
    
    print(f"\nMock User Summary: '{mock_summary}'")
    
    # 3. Generate the user profile vector
    print("Generating user profile embedding...")
    mock_profile = {
        "inferred": {
            "summary": mock_summary
        }
    }
    
    from app.vector.profile_vectors import user_profile_to_vector_async
    profile_vector = await user_profile_to_vector_async(mock_profile)
    
    # 4. Search for similar modules
    print("Searching for best matching modules...\n")
    from app.vector.vector_store import search_similar_modules
    results = search_similar_modules(profile_vector, top_k=5)
    
    recommendations = results.get("recommended", [])
    
    if not recommendations:
        print("No recommendations found.")
        return

    output = []
    output.append("TOP MATCHES:")
    output.append("-" * 60)
    for i, res in enumerate(recommendations):
        decoded = decode_module_id(res.id)
        match_line = f"{i+1}. Score: {res.score:.4f} | ID: {res.id:2} | Genre: {decoded['genre']:15} | Layout: {decoded['layout']}"
        output.append(match_line)
        # Get description
        from app.vector.module_vectors import get_module_by_id
        mod = get_module_by_id(res.id)
        if mod:
            output.append(f"   Description: {mod.description}")
        output.append("-" * 60)

    results_text = "\n".join(output)
    print(results_text)
    
    with open("matching_results.txt", "w") as f:
        f.write(f"Mock Summary: {mock_summary}\n\n")
        f.write(results_text)


if __name__ == "__main__":
    if not settings.OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY not found.")
        sys.exit(1)
    asyncio.run(test_module_matching())
