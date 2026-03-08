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


def module_to_text(module: ModuleMetadata) -> str:
    """
    Convert module metadata to highly discriminating searchable string.
    Removes the genre name itself to prevent keyword-bias matching,
    forcing similarity to rely on visual/mechanical trait overlapping.
    """
    tags_str = ", ".join(module.tags)
    return f"{module.description} Keywords: {tags_str}"


# Semantic Descriptions per Genre/Layout (Highly Discriminating Terminology)
DESCRIPTIONS = {
    "base": {
        "standard": "Standard commodity software UI. Generic functional patterns, system-default contrast, and conservative visual weighting with average alignment.",
        "compact": "Utility-first dense list view for basic data scanning. Default system-font styling with neutral technical focus.",
        "featured": "Generic highlight pattern using traditional bordering. Balanced density for standard promotional emphasis on neutral background.",
        "gallery": "Commodity grid layout with standard padding. Predictable image-to-text ratios for generic browsing experiences.",
        "technical": "Utility data sheet. Primary focus on tabular representation and standard legibility without any stylistic enhancements.",
        "bold": "Generic typographic emphasis. Standard bold headers over plain gray or white background containers.",
    },
    "minimalist": {
        "standard": "Ultra-low density design with massive whitespace. Crisp thin-weight typography, whisper-thin lines, and highly streamlined clinical aesthetic.",
        "compact": "Streamlined horizontal list item with high spatial gutters. Sophisticated thin typography and zero visual clutters or noise.",
        "featured": "Stark isolated product focus with extreme whitespace buffers. Clinical editorial layout featuring crisp, high-hierarchy thin typography.",
        "gallery": "Ultra-clean grid. High whitespace gutters and massive breathing room with lean lines and restrained information density.",
        "technical": "Architectural monospaced layout with clinical precision. High-contrast whitespace and minimal borders for a curated look.",
        "bold": "Editorial magazine layout with massive thin-weight headers. Premium low-density design with high whitespace and crisp visual hierarchy.",
    },
    "neobrutalist": {
        "standard": "Aggressive raw design system. Harsh high-contrast black borders, hard-offset drop shadows, and high-saturation flat primary colors. Anti-design aesthetic.",
        "compact": "High-contrast rigid bordering with thick black strokes. Saturated color blocks and unpolished hard-offset-shadow visual effects.",
        "featured": "Dissonant attention-grabbing layout with massive black outlines. Saturated clashing colors and raw brutalist visual energy and thick strokes.",
        "gallery": "Clipped image containers with hard black borders. Jagged layout patterns with high-contrast pop-art aesthetics and thick outlines.",
        "technical": "Raw HTML/System-default style with thick black borders. High-contrast monospaced information with aggressive styling and hard shadows.",
        "bold": "Huge black-outline typography. Saturated color backdrops with massive high-contrast strokes and raw unpolished aesthetic.",
    },
    "glassmorphism": {
        "standard": "Vibrant translucent frosted-glass panels with blurred textures. High-tech blur-behind effects and glowing light-diffused gradients with soft glows.",
        "compact": "Semi-transparent glowing glass bar. Diffused backlight effects with modern frosted surfacing and high-tech glass-blur layers.",
        "featured": "Massive glowing frosted glass pane with soft inner glows. Futuristic translucent layers and high-vibrancy color gradients with light diffusion.",
        "gallery": "Floating transparent glass cards with blurred background visibility. Multi-layered light-refracted surfaces and ethereal gradients with soft glows.",
        "technical": "Heads-up display (HUD) on translucent glass. Technical data-overlays with frosted textures and refined back-lighting and neon accents.",
        "bold": "Vibrant etched glass typography. Large headers on semi-transparent blurred surfaces with high-vibrancy glow effects and light diffusion.",
    },
    "loud": {
        "standard": "High-saturation energy neon gradients and aggressive chroma. Vibrant high-impact visuals with chaotic energy and loud visual density and massive noise.",
        "compact": "Condensed blast of high-saturation colors. Noisy high-energy density with aggressive vibrance and loud maximalist typographic focus.",
        "featured": "Explosive product spotlight using saturated neon gradients. Maximum visual noise and high-decibel design impact with vibration effects.",
        "gallery": "Glitch-filtered high-saturation images. Intense vibrant color chaos with energetic patterns and maximalist visual styling and neon noise.",
        "technical": "Neon-accented technical metrics. Frantic high-saturation markers and overwhelming energy with high-density visual markers and chaotic chroma.",
        "bold": "Maximalist streetwear aesthetic. Saturated background colors with screaming text and high-energy vibrant typography and massive visual noise.",
    },
    "cyber": {
        "standard": "Dark-mode technical terminal. Green/Neon phosphor scanline effects, monospaced fonts, and industrial hacker aesthetics with tactical UI.",
        "compact": "CLI-inspired horizontal output. Monospaced console text with high-tech system-default styling and dark-mode focus and phosphor glow.",
        "featured": "Complex dark-mode data hub. Intensive tactical UI with high-density monospaced metrics and futuristic system readouts and green neon.",
        "gallery": "Tactical image decoding interface. Dark-mode grid with industrial scanlines and high-tech terminal navigation and monospaced labels.",
        "technical": "Military-grade tactical readout. Dark background with high-density monospaced data and high-tech weaponry interface aesthetics and code-based UI.",
        "bold": "Industrial technical warnings. High-contrast dark-mode typography with technical alerts and futuristic sci-fi labels and tactical icons.",
    },
}

TAGS = {
    "base": ["standard-ui", "familiar", "neutral-contrast"],
    "minimalist": ["low-density", "high-whitespace", "thin-typography"],
    "neobrutalist": ["high-contrast", "thick-borders", "flat-color"],
    "glassmorphism": ["frosted-glass", "translucent", "blur-effect"],
    "loud": ["high-saturation", "vibrant-gradients", "intense-energy"],
    "cyber": ["dark-mode", "monospaced", "hud-layout"],
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
