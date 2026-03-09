"""
Module Vectors - Semantic feature vectors for all UI modules

Each module has a 1536-dimensional text embedding that captures its
visual and behavioral characteristics for similarity matching.

Module ID System (24 Modules):
- ID = (genre * 4) + bentoType
- This gives us 6 genres * 4 bento types = 24 unique modules
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

MODULES_PER_GENRE = 4

GENRE_MAP = {
    "glassmorphism": 0,
    "brutalism": 1,
    "neumorphism": 2,
    "cyberpunk": 3,
    "minimalist": 4,
    "monoprint": 5,
}

GENRE_NAMES = {v: k for k, v in GENRE_MAP.items()}

LAYOUT_MAP = {
    "hero": 0,
    "wide": 1,
    "tall": 2,
    "small": 3,
}

LAYOUT_NAMES = {v: k for k, v in LAYOUT_MAP.items()}


def encode_module_id(genre: str, layout: str) -> int:
    """Encode genre and layout into integer ID (0-23)"""
    g_idx = GENRE_MAP.get(genre, 0)
    l_idx = LAYOUT_MAP.get(layout, 0)
    return (g_idx * MODULES_PER_GENRE) + l_idx


def decode_module_id(module_id: int) -> dict:
    """Decode module ID to genre and layout"""
    genre_idx = module_id // MODULES_PER_GENRE
    layout_idx = module_id % MODULES_PER_GENRE

    return {
        "genre": GENRE_NAMES.get(genre_idx, "glassmorphism"),
        "layout": LAYOUT_NAMES.get(layout_idx, "hero"),
    }


class ModuleMetadata(BaseModel):
    """Module metadata with text embedding feature vector"""
    module_id: int
    layout: str
    genre: str
    description: str
    tags: List[str]

    # Feature vector (1536 dimensions for text-embedding-3-small)
    feature_vector: List[float] = Field(default_factory=lambda: [0.0] * FEATURE_DIMENSIONS)


def module_to_text(module: ModuleMetadata) -> str:
    """
    Convert module metadata to highly discriminating searchable string.
    Removes the genre name itself to prevent keyword-bias matching,
    forcing similarity to rely on visual/mechanical trait overlapping.
    """
    tags_str = ", ".join(module.tags)
    return f"{module.description} Keywords: {tags_str}"


# Semantic Descriptions per Genre/Layout (Bento Types from Drafting Site)
DESCRIPTIONS = {
    "glassmorphism": {
        "hero": "Large frosted-glass hero panel with translucent gradient background. Directional semi-transparent borders glow brighter on top and left edges. Product image fills 60% above centered bold serif title and accent-colored price on blurred dark premium backdrop.",
        "wide": "Horizontal frosted-glass split card with text on left and product image on right. Semi-transparent gradient surface with ethereal border glow, backdrop blur, and soft indigo accent price. Modern luxurious presentation with depth layering effects.",
        "tall": "Vertical frosted-glass column with product image stacked above content. Translucent gradient panel with directional border lighting and inset glow shadows. Text-shadowed title with accent-colored price on deep purple-blue blurred background.",
        "small": "Compact frosted-glass thumbnail card with small product image over minimal content. Semi-transparent gradient background with soft glowing borders and indigo price accent. Elegant minimized glass panel with backdrop blur depth.",
    },
    "brutalism": {
        "hero": "Large raw brutalist hero card with thick 3px black borders and hard 8px offset shadow. Pastel yellow background with product image bordered by heavy black stroke. Uppercase bold 900-weight title below. Red 'RAW / 01' badge in corner. Anti-design aggressive aesthetic.",
        "wide": "Horizontal brutalist split card with thick black borders and hard offset shadow. Pastel yellow background, text-left product-right layout. Uppercase heavy typography with yellow accent price. Red corner badge. Zero border-radius raw aesthetic.",
        "tall": "Vertical brutalist column with 3px black borders and 8px hard shadow. Product image with black bottom border above bold uppercase content. Pastel yellow background with aggressive high-contrast typography. Red 'RAW / 01' corner badge.",
        "small": "Compact brutalist thumbnail with thick black 3px borders and hard offset shadow. Sharp zero border-radius with pastel yellow background. Bold uppercase title and yellow price. Red tag badge. Raw anti-design pop-art energy.",
    },
    "neumorphism": {
        "hero": "Large soft-extruded hero card with subtle dual-direction shadows creating depth. Light #f8fafc background with transparent product image. Warm dark title with orange accent price displayed in inset-shadow pill. Soft plastic premium aesthetic.",
        "wide": "Horizontal soft-extruded split card with dual directional shadows. Light background with transparent product image on right. Dark-contrast title and orange inset-shadow price pill. Rounded 24px corners with premium raised surface feel.",
        "tall": "Vertical neumorphic column with extruded shadow on light background. Product image with transparent backdrop above dark text content. Orange accent price in recessed pill with inset shadows. Soft premium tactile surface aesthetic.",
        "small": "Compact neumorphic thumbnail with subtle dual shadows on light background. Transparent product image above dark title. Orange price in soft inset-shadow pill container. Rounded corners with clean raised-surface feel.",
    },
    "cyberpunk": {
        "hero": "Large dark cyberpunk hero with scanline repeating-gradient overlay. Cyan/teal semi-transparent border with subtle neon glow shadow. Transparent product image over near-black surface. Cyan glowing title with yellow accent price and left border pip. Futuristic terminal aesthetic.",
        "wide": "Horizontal dark cyberpunk card with scanline gradient texture. Cyan border with tech glow and transparent product image. Left-side cyan title with letter-spacing and neon text-shadow. Yellow price with left border accent. Dark grid-line underlayer.",
        "tall": "Vertical cyberpunk column with dark scanline background texture and cyan border glow. Product image on transparent dark surface above neon-colored title text. Yellow accent price with border-left pip. Futuristic hacker-terminal visual style.",
        "small": "Compact dark cyberpunk card with repeating scanline gradient and cyan border. Transparent product image above neon text. Yellow price accent with left pip border on near-black surface. Technical terminal miniature module.",
    },
    "minimalist": {
        "hero": "Large ultra-clean hero card with pure white background and near-invisible thin borders. Product image with multiply blend-mode on transparent surface with generous 2rem padding. Lightweight 300-weight lowercase title with very muted gray price. Expanding black underline on hover. Maximum negative space.",
        "wide": "Horizontal minimalist split card with white background and whisper-thin border. Product image with mix-blend-mode multiply. Centered lightweight lowercase title text and muted gray price. Zero border-radius with extreme whitespace. Hover reveals expanding underline.",
        "tall": "Vertical minimalist column with stark white background and barely visible border. Multiply-blended product image above centered lightweight lowercase title. Very muted gray price with generous whitespace buffers. Clean editorial clinical aesthetic.",
        "small": "Compact minimalist thumbnail with white background and ultra-thin border. Mix-blend-mode multiply on product image. Light-weight lowercase title and muted gray price. Zero border-radius with maximum breathing room. Hover expanding underline.",
    },
    "monoprint": {
        "hero": "Large dark monoprint hero card with #111 background and subtle radial dot-matrix pattern overlay. Product image on transparent dark background above Courier monospace title separated by thin #333 divider border. White price in monospace font. Industrial print-press aesthetic.",
        "wide": "Horizontal dark monoprint card with dot-matrix radial gradient pattern. #111 background with thin gray border. Product image on right, Courier monospace title on left separated by subtle content divider. White monospace price. Clean typographic print design.",
        "tall": "Vertical monoprint column with dark background and halftone dot-pattern overlay. Product image above monospace Courier title separated by thin #333 top-border. White monospace price on dark surface. Print-media industrial aesthetic with 4px border-radius.",
        "small": "Compact dark monoprint thumbnail with radial dot pattern overlay on #111 background. Courier New monospace title and white price below thin divider. Industrial newsprint-inspired compact module with subtle halftone texture.",
    },
}

TAGS = {
    "glassmorphism": ["frosted-glass", "translucent", "blur-effect", "gradient-border", "premium-depth"],
    "brutalism": ["thick-borders", "hard-shadow", "raw-badge", "uppercase", "high-contrast", "anti-design"],
    "neumorphism": ["soft-shadow", "extruded", "light-background", "inset-pill", "tactile", "premium-surface"],
    "cyberpunk": ["dark-mode", "scanline", "neon-glow", "cyan", "terminal", "futuristic"],
    "minimalist": ["whitespace", "lightweight-font", "multiply-blend", "underline-hover", "lowercase", "clinical"],
    "monoprint": ["dot-matrix", "dark-background", "monospace", "courier", "print-press", "industrial"],
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
    """Generate all 24 semantic modules (6 genres × 4 bento types)"""
    catalog = []
    for genre in GENRE_MAP.keys():
        for layout in LAYOUT_MAP.keys():
            catalog.append(create_module(genre, layout))
    return catalog


# The Complete 24-Module Catalog
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
    """Get modules by layout type (bento type)."""
    type_mapping = {
        "hero": "hero",
        "wide": "wide",
        "tall": "tall",
        "small": "small",
        "featured": "hero",
        "product-grid": "small",
        "cta": "wide",
    }
    layout = type_mapping.get(module_type.lower(), module_type.lower())
    return [m for m in MODULE_CATALOG if m.layout == layout]

def module_to_vector(metadata: ModuleMetadata) -> List[float]:
    """Return the generated embedding from module metadata"""
    return metadata.feature_vector
