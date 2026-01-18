"""
Module Vectors - Pre-computed feature vectors for all UI modules

Each module has a 12-dimensional feature vector that captures its
visual and behavioral characteristics for similarity matching.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from app.vector.feature_schema import (
    FEATURE_DIMENSIONS,
    FeatureVector,
    FeatureIndex,
    GENRE_VECTORS,
    normalize_vector,
)


class ModuleMetadata(BaseModel):
    """Extended module metadata with feature vector"""
    module_id: str
    module_type: str  # hero, product-grid, cta, banner, etc.
    genre: str        # minimalist, neobrutalist, glassmorphism, etc.
    variant: str      # v1, v2, soft, bold, etc.
    
    # Feature vector (12 dimensions)
    feature_vector: List[float] = Field(default_factory=lambda: [0.5] * FEATURE_DIMENSIONS)
    
    # Human-readable feature descriptions
    tags: List[str] = Field(default_factory=list)
    
    # Explicit feature overrides (0-1 range)
    darkness: float = 0.5
    vibrancy: float = 0.5
    corner_roundness: float = 0.5
    density: float = 0.5
    typography_weight: float = 0.5
    button_size: float = 0.5
    interactivity: float = 0.5
    
    def compute_vector(self) -> List[float]:
        """Compute the full feature vector from module properties"""
        vector = [0.0] * FEATURE_DIMENSIONS
        
        # Visual features
        vector[FeatureIndex.DARKNESS] = self.darkness
        vector[FeatureIndex.VIBRANCY] = self.vibrancy
        vector[FeatureIndex.CORNER_ROUNDNESS] = self.corner_roundness
        vector[FeatureIndex.DENSITY] = self.density
        vector[FeatureIndex.TYPOGRAPHY_WEIGHT] = self.typography_weight
        vector[FeatureIndex.BUTTON_SIZE] = self.button_size
        
        # Genre features
        genre_vec = GENRE_VECTORS.get(self.genre, [0.0, 0.0, 0.0, 0.2])
        vector[FeatureIndex.MINIMALISM] = genre_vec[0]
        vector[FeatureIndex.BRUTALISM] = genre_vec[1]
        vector[FeatureIndex.GLASS_EFFECT] = genre_vec[2]
        vector[FeatureIndex.LOUDNESS] = genre_vec[3]
        
        # Behavioral features
        vector[FeatureIndex.INTERACTIVITY] = self.interactivity
        vector[FeatureIndex.EXPLORATION] = genre_vec[3]  # Loud = exploratory
        
        self.feature_vector = vector
        return vector


def module_to_vector(metadata: ModuleMetadata) -> FeatureVector:
    """Convert module metadata to normalized feature vector"""
    vector = metadata.compute_vector()
    return normalize_vector(vector)


# Pre-defined module catalog with feature vectors
MODULE_CATALOG: List[ModuleMetadata] = [
    # ========================================
    # HERO MODULES
    # ========================================
    ModuleMetadata(
        module_id="hero_base_v1",
        module_type="hero",
        genre="base",
        variant="v1",
        tags=["hero", "full-width", "standard"],
        darkness=0.3, vibrancy=0.4, corner_roundness=0.5,
        density=0.5, typography_weight=0.5, button_size=0.5,
        interactivity=0.4,
    ),
    ModuleMetadata(
        module_id="hero_minimalist_v1",
        module_type="hero",
        genre="minimalist",
        variant="v1",
        tags=["hero", "clean", "whitespace"],
        darkness=0.0, vibrancy=0.1, corner_roundness=0.0,
        density=0.2, typography_weight=0.3, button_size=0.4,
        interactivity=0.2,
    ),
    ModuleMetadata(
        module_id="hero_neobrutalist_v1",
        module_type="hero",
        genre="neobrutalist",
        variant="v1",
        tags=["hero", "bold", "raw", "high-contrast"],
        darkness=0.1, vibrancy=0.9, corner_roundness=0.0,
        density=0.7, typography_weight=1.0, button_size=0.8,
        interactivity=0.6,
    ),
    ModuleMetadata(
        module_id="hero_glassmorphism_v1",
        module_type="hero",
        genre="glassmorphism",
        variant="v1",
        tags=["hero", "blur", "translucent", "dreamy"],
        darkness=0.3, vibrancy=0.5, corner_roundness=0.8,
        density=0.4, typography_weight=0.4, button_size=0.5,
        interactivity=0.7,
    ),
    ModuleMetadata(
        module_id="hero_loud_v1",
        module_type="hero",
        genre="loud",
        variant="v1",
        tags=["hero", "experimental", "gradient", "attention"],
        darkness=0.2, vibrancy=1.0, corner_roundness=0.7,
        density=0.6, typography_weight=0.8, button_size=0.7,
        interactivity=0.9,
    ),
    ModuleMetadata(
        module_id="hero_cyber_v1",
        module_type="hero",
        genre="cyber",
        variant="v1",
        tags=["hero", "matrix", "terminal", "hacker"],
        darkness=0.95, vibrancy=0.7, corner_roundness=0.1,
        density=0.5, typography_weight=0.5, button_size=0.5,
        interactivity=0.8,
    ),
    
    # ========================================
    # PRODUCT GRID MODULES
    # ========================================
    ModuleMetadata(
        module_id="grid_base_v1",
        module_type="product-grid",
        genre="base",
        variant="v1",
        tags=["grid", "products", "standard"],
        darkness=0.3, vibrancy=0.4, corner_roundness=0.5,
        density=0.5, typography_weight=0.5, button_size=0.5,
        interactivity=0.5,
    ),
    ModuleMetadata(
        module_id="grid_minimalist_v1",
        module_type="product-grid",
        genre="minimalist",
        variant="v1",
        tags=["grid", "clean", "sparse"],
        darkness=0.0, vibrancy=0.1, corner_roundness=0.0,
        density=0.2, typography_weight=0.3, button_size=0.3,
        interactivity=0.2,
    ),
    ModuleMetadata(
        module_id="grid_neobrutalist_v1",
        module_type="product-grid",
        genre="neobrutalist",
        variant="v1",
        tags=["grid", "bold", "chunky"],
        darkness=0.1, vibrancy=0.9, corner_roundness=0.0,
        density=0.8, typography_weight=0.9, button_size=0.8,
        interactivity=0.5,
    ),
    ModuleMetadata(
        module_id="grid_glassmorphism_v1",
        module_type="product-grid",
        genre="glassmorphism",
        variant="v1",
        tags=["grid", "blur", "cards"],
        darkness=0.3, vibrancy=0.5, corner_roundness=0.8,
        density=0.4, typography_weight=0.4, button_size=0.5,
        interactivity=0.6,
    ),
    
    # ========================================
    # CTA MODULES  
    # ========================================
    ModuleMetadata(
        module_id="cta_base_v1",
        module_type="cta",
        genre="base",
        variant="v1",
        tags=["cta", "action", "standard"],
        darkness=0.3, vibrancy=0.5, corner_roundness=0.5,
        density=0.5, typography_weight=0.6, button_size=0.6,
        interactivity=0.5,
    ),
    ModuleMetadata(
        module_id="cta_minimalist_v1",
        module_type="cta",
        genre="minimalist",
        variant="v1",
        tags=["cta", "subtle", "clean"],
        darkness=0.0, vibrancy=0.1, corner_roundness=0.0,
        density=0.3, typography_weight=0.4, button_size=0.4,
        interactivity=0.3,
    ),
    ModuleMetadata(
        module_id="cta_loud_v1",
        module_type="cta",
        genre="loud",
        variant="v1",
        tags=["cta", "urgent", "attention", "high-contrast"],
        darkness=0.2, vibrancy=1.0, corner_roundness=0.8,
        density=0.6, typography_weight=0.9, button_size=0.9,
        interactivity=0.9,
    ),
    
    # ========================================
    # BANNER MODULES
    # ========================================
    ModuleMetadata(
        module_id="banner_base_v1",
        module_type="banner",
        genre="base",
        variant="v1",
        tags=["banner", "notification", "info"],
        darkness=0.3, vibrancy=0.4, corner_roundness=0.3,
        density=0.4, typography_weight=0.5, button_size=0.4,
        interactivity=0.3,
    ),
    ModuleMetadata(
        module_id="banner_loud_v1",
        module_type="banner",
        genre="loud",
        variant="v1",
        tags=["banner", "sale", "urgent"],
        darkness=0.1, vibrancy=1.0, corner_roundness=0.5,
        density=0.5, typography_weight=0.8, button_size=0.5,
        interactivity=0.7,
    ),
]

# Pre-compute all module vectors
def initialize_module_vectors():
    """Compute and store vectors for all modules"""
    for module in MODULE_CATALOG:
        module.compute_vector()

# Initialize on import
initialize_module_vectors()


def get_module_by_id(module_id: str) -> Optional[ModuleMetadata]:
    """Get module metadata by ID"""
    for module in MODULE_CATALOG:
        if module.module_id == module_id:
            return module
    return None


def get_modules_by_type(module_type: str) -> List[ModuleMetadata]:
    """Get all modules of a specific type"""
    return [m for m in MODULE_CATALOG if m.module_type == module_type]
