"""
Profile Vectors - Convert user profiles to text embeddings

Embeds inferred user profiles using Gemini to match against module descriptions.
Implements 80/20 Exploitation/Exploration for automated A/B testing.
"""

import random
from typing import List, Tuple
import asyncio
import logging
import hashlib
from app.vector.feature_schema import FEATURE_DIMENSIONS, FeatureVector, normalize_vector
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)

# Exploration rate: 20% of recommendations are exploratory (non-optimal genre)
EXPLORE_RATE = 0.20


async def user_profile_to_vector_async(profile_dict: dict) -> FeatureVector:
    """
    Convert a UserProfile dict directly to a text embedding.
    Uses the new vibe_summary field. Implements Exact Match Caching.
    """
    from app.config import settings

    if isinstance(profile_dict, str):
        summary = profile_dict
    else:
        summary = profile_dict.get("vibe_summary", "New user seeking a standard, clean experience.")

    # Check cache first
    summary_hash = hashlib.md5(summary.encode()).hexdigest()
    cache_key = f"profile_embed:{summary_hash}"
    cached_vec = await cache_service.get(cache_key)

    if cached_vec and len(cached_vec) == FEATURE_DIMENSIONS:
        return cached_vec

    if not settings.OPENROUTER_API_KEY:
        logger.warning("No OPENROUTER_API_KEY. Using zero vector for profile.")
        return [0.0] * FEATURE_DIMENSIONS

    try:
        from langchain_openai import OpenAIEmbeddings
        embeddings_model = OpenAIEmbeddings(
            model="openai/text-embedding-3-small",
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None, lambda: embeddings_model.embed_query(summary)
        )

        normalized_vec = normalize_vector(embedding)

        # Cache for 24 hours
        await cache_service.set(cache_key, normalized_vec, ttl=86400)

        return normalized_vec
    except Exception as e:
        logger.error(f"Failed to embed user profile: {e}")
        return [0.0] * FEATURE_DIMENSIONS


async def get_recommended_template_id_async(profile_dict: dict) -> Tuple[int, bool]:
    """
    Get the recommended integer Template ID for a user profile.

    Implements 80/20 Exploitation/Exploration:
    - 80% EXPLOIT: return the top-matching module ID
    - 20% EXPLORE: return a module from a randomly selected DIFFERENT genre

    Returns:
        (module_id, is_explore) tuple
        is_explore=True means this was a deliberate exploratory recommendation
    """
    from app.vector.vector_store import search_similar_modules, vector_store
    from app.vector.module_vectors import decode_module_id, GENRE_MAP, MODULES_PER_GENRE

    # Convert profile to vector
    profile_vec = await user_profile_to_vector_async(profile_dict)

    # Query vector store for similar modules (search all 24)
    results = search_similar_modules(profile_vec, top_k=5)
    recommendations = results.get("recommended", [])

    if not recommendations:
        return 0, False

    # Log top matches
    print(f"[Vector] Top {len(recommendations)} matches:")
    for i, result in enumerate(recommendations[:3]):
        decoded = decode_module_id(result.id)
        print(
            f"  {i+1}. ID={result.id} ({decoded['genre']}/{decoded['layout']}) score={result.score:.4f}"
        )

    top_result = recommendations[0]
    exploit_id = top_result.id
    exploit_genre = decode_module_id(exploit_id).get("genre", "glassmorphism")

    # ─── 80/20 EXPLOITATION / EXPLORATION ───────────────────────────────────
    is_explore = random.random() < EXPLORE_RATE

    if is_explore:
        # Pick a random genre that is NOT the optimal genre
        all_genres = list(GENRE_MAP.keys())
        alt_genres = [g for g in all_genres if g != exploit_genre]
        explore_genre = random.choice(alt_genres)

        # Pick a random layout within that genre (0–3)
        explore_layout_idx = random.randint(0, 3)
        explore_id = GENRE_MAP[explore_genre] * MODULES_PER_GENRE + explore_layout_idx

        logger.info(
            f"[Explore] EXPLORE branch selected: {explore_genre} (ID={explore_id}) "
            f"vs optimal {exploit_genre} (ID={exploit_id})"
        )
        return explore_id, True

    # Standard exploitation path
    return exploit_id, False


async def get_recommended_genre_async(profile_dict: dict) -> str:
    """
    Get the recommended genre for a user profile.
    """
    from app.vector.vector_store import search_similar_modules
    from app.vector.vector_store import vector_store

    profile_vec = await user_profile_to_vector_async(profile_dict)
    results = search_similar_modules(profile_vec, top_k=1)

    recommendations = results.get("recommended", [])
    if recommendations:
        metadata = vector_store.metadata.get(recommendations[0].id, {})
        return metadata.get("genre", "glassmorphism")

    return "glassmorphism"
