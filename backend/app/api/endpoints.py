from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.models.product import Product
from app.models.telemetry import MotorTelemetry, TelemetryEventsBatch
from app.models.visual_features import (
    Genre, 
    VisualFeatureVector,
    get_visual_feature_vector,
    get_all_visual_feature_vectors,
    FEATURE_DIMENSIONS
)
from app.services.product_service import product_service
from app.services.telemetry_service import telemetry_service

router = APIRouter()

@router.get("/products/{session_id}", response_model=List[Product])
async def get_products(session_id: str):
    # TODO: Load persistent user preferences using session_id
    return product_service.get_products_for_session(session_id)

# ============================================
# VISUAL FEATURES ENDPOINTS
# ============================================

@router.get("/visual-features", tags=["Visual Features"])
async def get_all_visual_features() -> Dict[str, Any]:
    """
    Get visual feature vectors for all 6 genres.
    Each vector has 11 numerical dimensions for ML vectorization.
    """
    vectors = get_all_visual_feature_vectors()
    return {
        "count": len(vectors),
        "dimensions": FEATURE_DIMENSIONS,
        "vectors": [v.to_dict() for v in vectors]
    }

@router.get("/visual-features/{genre_id}", tags=["Visual Features"])
async def get_visual_features_by_genre(genre_id: int) -> Dict[str, Any]:
    """
    Get visual feature vector for a specific genre (0-5).
    
    Genres:
    - 0: Base
    - 1: Minimalist
    - 2: Neobrutalist
    - 3: Glassmorphism
    - 4: Loud
    - 5: Cyber
    """
    if genre_id < 0 or genre_id > 5:
        raise HTTPException(status_code=400, detail="Genre ID must be 0-5")
    
    genre = Genre(genre_id)
    vector = get_visual_feature_vector(genre)
    
    return {
        "genre_id": genre_id,
        "vector": vector.to_dict(),
        "array": vector.to_array()
    }

# @router.post("/telemetry/motor")
# async def post_motor_telemetry(data: MotorTelemetry):
#     return await telemetry_service.process_motor_telemetry(data)

# @router.post("/telemetry/events")
# async def post_events_telemetry(data: TelemetryEventsBatch):
#     # TODO: Identify if this session should be merged with an existing user profile for persistence
#     return await telemetry_service.process_events_telemetry(data)

