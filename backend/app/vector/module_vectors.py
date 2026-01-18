"""
Module Vectors - Pre-computed feature vectors for all UI modules

Each module has a 12-dimensional feature vector that captures its
visual and behavioral characteristics for similarity matching.

Module ID System (36 Modules):
- ID = (genre * 6) + layout
- This gives us 6 genres × 6 layouts = 36 unique modules
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


# ============================================
# ID ENCODING (Matches Frontend)
# ============================================

# Constants
MODULES_PER_GENRE = 6

# Genre Mappings (0-5)
GENRE_MAP = {
    "base": 0,
    "minimalist": 1,
    "neobrutalist": 2,
    "glassmorphism": 3,
    "loud": 4,
    "cyber": 5
}

GENRE_NAMES = {v: k for k, v in GENRE_MAP.items()}

# Layout Mappings (0-5)
LAYOUT_MAP = {
    "standard": 0,   # Standard Card
    "compact": 1,    # Compact / List
    "featured": 2,   # Featured / Heroic
    "gallery": 3,    # Gallery / Visual
    "technical": 4,  # Technical / Data
    "bold": 5        # Typographic / Bold
}

LAYOUT_NAMES = {v: k for k, v in LAYOUT_MAP.items()}


def encode_module_id(genre: str, layout: str) -> int:
    """
    Encode genre and layout into integer ID (0-35)
    Formula: (genre * 6) + layout
    """
    g_idx = GENRE_MAP.get(genre, 0)
    l_idx = LAYOUT_MAP.get(layout, 0)
    return (g_idx * MODULES_PER_GENRE) + l_idx


def decode_module_id(module_id: int) -> dict:
    """Decode module ID to genre and layout"""
    genre_idx = module_id // MODULES_PER_GENRE
    layout_idx = module_id % MODULES_PER_GENRE
    
    return {
        "genre": GENRE_NAMES.get(genre_idx, "base"),
        "layout": LAYOUT_NAMES.get(layout_idx, "standard")
    }


class ModuleMetadata(BaseModel):
    """Extended module metadata with feature vector"""
    module_id: int
    layout: str  
    genre: str        
    description: str
    tags: List[str]
    
    # Feature vector (12 dimensions)
    feature_vector: List[float] = Field(default_factory=lambda: [0.5] * FEATURE_DIMENSIONS)
    
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


# ============================================
# GENRE FEATURE PROFILES
# ============================================

GENRE_PROFILES = {
    "base": {
        "darkness": 0.3, "vibrancy": 0.4, "corner_roundness": 0.5,
        "density": 0.5, "typography_weight": 0.5, "button_size": 0.5,
        "interactivity": 0.4
    },
    "minimalist": {
        "darkness": 0.0, "vibrancy": 0.1, "corner_roundness": 0.0,
        "density": 0.2, "typography_weight": 0.3, "button_size": 0.4,
        "interactivity": 0.2
    },
    "neobrutalist": {
        "darkness": 0.1, "vibrancy": 0.9, "corner_roundness": 0.0,
        "density": 0.8, "typography_weight": 1.0, "button_size": 0.8,
        "interactivity": 0.6
    },
    "glassmorphism": {
        "darkness": 0.3, "vibrancy": 0.5, "corner_roundness": 0.8,
        "density": 0.4, "typography_weight": 0.4, "button_size": 0.5,
        "interactivity": 0.7
    },
    "loud": {
        "darkness": 0.2, "vibrancy": 1.0, "corner_roundness": 0.7,
        "density": 0.6, "typography_weight": 0.8, "button_size": 0.7,
        "interactivity": 0.9
    },
    "cyber": {
        "darkness": 0.95, "vibrancy": 0.7, "corner_roundness": 0.1,
        "density": 0.5, "typography_weight": 0.5, "button_size": 0.5,
        "interactivity": 0.8
    }
}

# Layout feature modifications
LAYOUT_MODIFIERS = {
    "standard": {},
    "compact": {"density": 0.8, "button_size": 0.3},
    "featured": {"density": 0.3, "button_size": 0.7, "vibrancy": 0.1}, # +0.1 vibrancy
    "gallery": {"density": 0.2, "interactivity": 0.8},
    "technical": {"density": 0.9, "typography_weight": 0.2},
    "bold": {"typography_weight": 0.9, "vibrancy": 0.1}
}

# Semantic Descriptions per Genre/Layout
DESCRIPTIONS = {
    "base": {
        "standard": "A clean, standard product card with a white background and subtle shadow. Trustworthy and familiar.",
        "compact": "A simple horizontal list item for easy scanning. Efficient and unobtrusive.",
        "featured": "A highlighted product card with slightly larger image and emphasis. Good for promotions.",
        "gallery": "A minimalist image-focused card with details revealed on hover.",
        "technical": "A detailed card showing product specs clearly arranged. informative.",
        "bold": "A card with larger typography for the title, emphasizing the name."
    },
    "minimalist": {
        "standard": "A stark white card with zero borders and ample whitespace. Feels like a high-end art gallery.",
        "compact": "A razor-sharp horizontal layout with fine lines and perfect alignment.",
        "featured": "A massive isolated image with tiny, sophisticated typography floating next to it.",
        "gallery": "A pure image block. No text visible until interaction. Complete visual immersion.",
        "technical": "Specs laid out in a fine grid with mono-spaced tiny fonts. Architectural feel.",
        "bold": "Title written in large, thin Helvetica. Very editorial and magazine-like."
    },
    "neobrutalist": {
        "standard": "A bold card with thick black borders, hard offset shadow, and punchy yellow accents. Playful and raw.",
        "compact": "A horizontal strip with distinct bordered compartments for every data point.",
        "featured": "A loud, attention-grabbing box with clashing colors and massive borders. Cannot be ignored.",
        "gallery": "Image trapped inside a thick window frame. Hover distorts the image or shifts colors.",
        "technical": "Data points look like raw HTML inputs or database entries. Very unpolished aesthetic.",
        "bold": "Title text is massive, black, and possibly outlined. Feels like a protest poster."
    },
    "glassmorphism": {
        "standard": "A translucent frosted glass card floating over a soft gradient. Ethereal and premium.",
        "compact": "A slim glass bar that blurs the background as it scrolls. Delicate and futuristic.",
        "featured": "A large glowing glass pane with soft inner light. Feels expensive and high-tech.",
        "gallery": "Images have soft, blurred edges and float in space. No hard lines anywhere.",
        "technical": "Data is displayed on a 'heads-up display' (HUD) style glass interface.",
        "bold": "Typography seems to be etched into the glass surface. Subtle but large."
    },
    "loud": {
        "standard": "A high-energy card using vibrant gradients and aggressive motion. Demands attention.",
        "compact": "A condensed blast of color and bold text. Efficient but noisy.",
        "featured": "Explodes off the screen with parallax effects and neon colors. Maximum impact.",
        "gallery": "Images are heavily treated with filters or duo-tone gradients until hovered.",
        "technical": "Specs are highlighted with neon markers and frantic energy.",
        "bold": "Text covers the entire image in a massive, poster-style treatment. Street-wear vibe."
    },
    "cyber": {
        "standard": "A dark terminal window with green phosphor text and scanlines. Hacker aesthetic.",
        "compact": "A command-line style list entry using monospaced fonts and blinking cursors.",
        "featured": "A large mainframe display look. Complex data visualizations surround the product.",
        "gallery": "Images look like they are being decoded or downloaded line by line.",
        "technical": "The ultimate specs card. Looks like a weapon readout in a sci-fi game.",
        "bold": "Typography looks like warning labels or system alerts. Industrial sci-fi."
    }
}

TAGS = {
    "base": ["classic", "reliable", "clean"],
    "minimalist": ["luxury", "premium", "stark"],
    "neobrutalist": ["playful", "bold", "raw"],
    "glassmorphism": ["ethereal", "dreamy", "modern"],
    "loud": ["energetic", "vibrant", "intense"],
    "cyber": ["technical", "dark", "hacker"]
}


def create_module(genre: str, layout: str) -> ModuleMetadata:
    """Create a module with proper encoding and genre-based features"""
    profile = GENRE_PROFILES.get(genre, GENRE_PROFILES["base"]).copy()
    
    # Apply layout modifiers
    modifiers = LAYOUT_MODIFIERS.get(layout, {})
    for key, delta in modifiers.items():
        if key in profile:
            profile[key] = max(0.0, min(1.0, profile[key] + delta))
            
    # Get description and tags
    desc = DESCRIPTIONS.get(genre, {}).get(layout, "Standard product module.")
    genre_tags = TAGS.get(genre, [])
    layout_tag = layout
    all_tags = genre_tags + [layout_tag]
    
    return ModuleMetadata(
        module_id=encode_module_id(genre, layout),
        layout=layout,
        genre=genre,
        description=desc,
        tags=all_tags,
        **profile
    )


def generate_catalog() -> List[ModuleMetadata]:
    """Generate all 36 semantic modules"""
    catalog = []
    
    for genre in GENRE_MAP.keys():
        for layout in LAYOUT_MAP.keys():
            catalog.append(create_module(genre, layout))
            
    return catalog


# The Complete 36-Module Catalog
MODULE_CATALOG: List[ModuleMetadata] = generate_catalog()


# Pre-compute all module vectors
def initialize_module_vectors():
    """Compute and store vectors for all modules"""
    for module in MODULE_CATALOG:
        module.compute_vector()
    
    print(f"[ModuleVectors] Catalog initialized with {len(MODULE_CATALOG)} modules")


def get_module_by_id(module_id: int) -> Optional[ModuleMetadata]:
    """Get module metadata by ID"""
    for module in MODULE_CATALOG:
        if module.module_id == module_id:
            return module
    return None


def get_modules_by_type(module_type: str) -> List[ModuleMetadata]:
    """
    Get modules by layout type.
    
    Args:
        module_type: Layout type (e.g., 'hero', 'product-grid', 'cta', 'standard', 'featured')
    
    Returns:
        List of modules matching the layout type
    """
    # Map common type names to layout names
    type_mapping = {
        "hero": "featured",
        "product-grid": "gallery",
        "cta": "bold",
        "standard": "standard",
        "compact": "compact",
        "featured": "featured",
        "gallery": "gallery",
        "technical": "technical",
        "bold": "bold",
    }
    
    layout = type_mapping.get(module_type.lower(), module_type.lower())
    
    return [m for m in MODULE_CATALOG if m.layout == layout]
