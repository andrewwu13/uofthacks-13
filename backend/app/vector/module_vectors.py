"""
Module Vectors - Semantic feature vectors for all UI modules

Each module has a 768-dimensional text embedding that captures its
visual and behavioral characteristics for similarity matching.

Module ID System (36 Modules):
- ID = (genre * 6) + layout
- This gives us 6 genres * 6 layouts = 36 unique modules
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import os
import logging
import asyncio
from app.vector.feature_schema import FEATURE_DIMENSIONS

logger = logging.getLogger(__name__)

# ============================================
# ID ENCODING (Matches Frontend)
# ============================================

MODULES_PER_GENRE = 6

GENRE_MAP = {
    "base": 0,
    "minimalist": 1,
    "neobrutalist": 2,
    "glassmorphism": 3,
    "loud": 4,
    "cyber": 5,
}

GENRE_NAMES = {v: k for k, v in GENRE_MAP.items()}

LAYOUT_MAP = {
    "standard": 0,
    "compact": 1,
    "featured": 2,
    "gallery": 3,
    "technical": 4,
    "bold": 5,
}

LAYOUT_NAMES = {v: k for k, v in LAYOUT_MAP.items()}


def encode_module_id(genre: str, layout: str) -> int:
    """Encode genre and layout into integer ID (0-35)"""
    g_idx = GENRE_MAP.get(genre, 0)
    l_idx = LAYOUT_MAP.get(layout, 0)
    return (g_idx * MODULES_PER_GENRE) + l_idx


def decode_module_id(module_id: int) -> dict:
    """Decode module ID to genre and layout"""
    genre_idx = module_id // MODULES_PER_GENRE
    layout_idx = module_id % MODULES_PER_GENRE

    return {
        "genre": GENRE_NAMES.get(genre_idx, "base"),
        "layout": LAYOUT_NAMES.get(layout_idx, "standard"),
    }


class ModuleMetadata(BaseModel):
    """Module metadata with text embedding feature vector"""
    module_id: int
    layout: str
    genre: str
    description: str
    tags: List[str]

    # Feature vector (768 dimensions for Gemini API embeddings)
    feature_vector: List[float] = Field(default_factory=lambda: [0.0] * FEATURE_DIMENSIONS)


# Semantic Descriptions per Genre/Layout (Short, Punchy Vibes)
DESCRIPTIONS = {
    "base": {
        "standard": "Clean and trustworthy standard product card. Functional, familiar, no surprises.",
        "compact": "Efficient horizontal list item. High density for easy scanning. Unobtrusive.",
        "featured": "Prominent highlighted product card. Designed to gently emphasize promotions.",
        "gallery": "Minimalist image-focused view. Details reveal slowly. Clean presentation.",
        "technical": "Data-heavy informative layout. Specs and details are front and center.",
        "bold": "Typographic emphasis. Large, readable text over subtle backgrounds.",
    },
    "minimalist": {
        "standard": "Stark white, zero borders, ample whitespace. High-end art gallery feeling.",
        "compact": "Razor-sharp, airy horizontal strip. Perfect alignment and whisper-thin lines.",
        "featured": "Massive isolated image. Tiny, sophisticated luxury typography floating nearby.",
        "gallery": "Pure image block. Subdued text on interaction. Total visual immersion.",
        "technical": "Architectural grid of mono-spaced tiny text. Stark, calculated, precise.",
        "bold": "Large, ultra-thin Helvetica-style text. Premium editorial magazine layout.",
    },
    "neobrutalist": {
        "standard": "Thick black borders, hard offset shadows, punchy flat colors. Raw and playful.",
        "compact": "Distinct rigid boxes for data. High contrast horizontal strip. Clunky but fun.",
        "featured": "Aggressive, attention-grabbing box. Clashing colors and massive borders. Unignorable.",
        "gallery": "Image trapped in a thick window frame. Hover effects are distorted and jagged.",
        "technical": "Unpolished aesthetic. Looks like raw HTML inputs or raw database entries.",
        "bold": "Massive, black, outline text. Looks like a chaotic protest poster or zine.",
    },
    "glassmorphism": {
        "standard": "Translucent frosted glass floating over a soft pastel gradient. Ethereal and premium.",
        "compact": "Delicate, slim glass bar blurring the background. Futuristic and gentle.",
        "featured": "Large glowing pane with soft inner light. High-tech, expensive, smooth.",
        "gallery": "Soft, blurred edges floating in space. Dreamy, no hard lines anywhere.",
        "technical": "Heads-up display (HUD) style. Semi-transparent data overlays on glass.",
        "bold": "Subtle but large typography etched directly into the frosted glass surface.",
    },
    "loud": {
        "standard": "Vibrant gradients, high contrast, aggressive energy. Demands your immediate attention.",
        "compact": "Condensed blast of intense color and bold text. Extremely noisy and fast.",
        "featured": "Explodes off the screen. Neon colors and maximum visual impact. Overwhelming.",
        "gallery": "Heavily treated duo-tone or glitch-filtered images. Very intense visuals.",
        "technical": "Specs highlighted with neon markers. Frantic energy and chaotic layout.",
        "bold": "Massive streetwear poster vibe. Screaming text covering entire backgrounds.",
    },
    "cyber": {
        "standard": "Dark terminal window with green phosphor text and scanlines. Hacker aesthetic.",
        "compact": "Command-line style output. Monospaced fonts and blinking cursors.",
        "featured": "Mainframe complex data visualization. Very dark, intense, high-tech.",
        "gallery": "Images look like they are actively decoding or downloading line by line.",
        "technical": "Weapon readout interface from a sci-fi game. Dark mode, dense, tactical.",
        "bold": "System alert warning labels. Industrial sci-fi typography and high contrast.",
    },
}

TAGS = {
    "base": ["classic", "reliable", "clean"],
    "minimalist": ["luxury", "premium", "stark"],
    "neobrutalist": ["playful", "bold", "raw"],
    "glassmorphism": ["ethereal", "dreamy", "modern"],
    "loud": ["energetic", "vibrant", "intense"],
    "cyber": ["technical", "dark", "hacker"],
}


def create_module(genre: str, layout: str) -> ModuleMetadata:
    """Create a module with proper description and tags"""
    desc = DESCRIPTIONS.get(genre, {}).get(layout, "Standard product module.")
    genre_tags = TAGS.get(genre, [])
    
    return ModuleMetadata(
        module_id=encode_module_id(genre, layout),
        layout=layout,
        genre=genre,
        description=desc,
        tags=genre_tags + [layout],
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


async def initialize_module_vectors_async():
    """Compute and store text embeddings for all modules dynamically using Gemini"""
    from app.config import settings
    
    if not settings.OPENROUTER_API_KEY:
        logger.warning("No OPENROUTER_API_KEY found. Generating dummy vectors instead.")
        return

    try:
        from langchain_openai import OpenAIEmbeddings
        embeddings_model = OpenAIEmbeddings(
            model="openai/text-embedding-3-small",
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        
        logger.info(f"[ModuleVectors] Generating embeddings for {len(MODULE_CATALOG)} modules via OpenRouter...")
        
        texts = [m.description for m in MODULE_CATALOG]
        
        # Run in executor to avoid event loop blocking
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None, lambda: embeddings_model.embed_documents(texts)
        )
        
        for i, module in enumerate(MODULE_CATALOG):
            module.feature_vector = embeddings[i]
            
        logger.info("[ModuleVectors] Successfully generated semantic embeddings for all modules.")
            
    except Exception as e:
        logger.error(f"[ModuleVectors] Failed to generate embeddings: {e}")

def get_module_by_id(module_id: int) -> Optional[ModuleMetadata]:
    """Get module metadata by ID"""
    for module in MODULE_CATALOG:
        if module.module_id == module_id:
            return module
    return None

def get_modules_by_type(module_type: str) -> List[ModuleMetadata]:
    """Get modules by layout type."""
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

def module_to_vector(metadata: ModuleMetadata) -> List[float]:
    """Return the generated embedding from module metadata"""
    return metadata.feature_vector
