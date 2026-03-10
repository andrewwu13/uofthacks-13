/**
 * Gen UI Schema Types
 * 
 * Module ID System (1:1 with backend - 24 modules):
 * Each module has a unique ID that encodes:
 * - Genre (0-5): The visual style (glassmorphism, brutalism, etc.)
 * - BentoType (0-3): The bento grid size (hero, wide, tall, small)
 * 
 * ID = (genre * 4) + bentoType
 * This gives us 6 × 4 = 24 unique bento module templates (0-23)
 * 
 * Semantic Module IDs: mod-{genre}-{bentoType}-{instanceId}
 * Example: mod-glassmorphism-hero-001
 */

// ============================================
// LAYOUT SCHEMA TYPES (from main branch)
// ============================================

export interface DesignTokenOverrides {
  colors?: Record<string, string>;
  typography?: Record<string, string>;
  spacing?: Record<string, string>;
  borderRadius?: Record<string, string>;
}

export interface LayoutModule {
  id: string;
  type: string;
  genre: 'base' | 'minimalist' | 'neobrutalist' | 'glassmorphism' | 'loud';
  props?: Record<string, any>;
  data?: Record<string, any>;
  variants?: Record<string, any>;
}

export interface LayoutSection {
  id: string;
  type: string; // e.g., 'full-width', 'container', 'grid'
  modules: LayoutModule[];
  styles?: Record<string, string>;
}

export interface LayoutSchema {
  id: string;
  name: string;
  sections: LayoutSection[];
  design_system_overrides?: DesignTokenOverrides;
}

// Module Props Interfaces (from main branch)

export interface HeroProps {
  id: string;
  title: string;
  subtitle: string;
  backgroundImage?: string;
  ctaText?: string;
  ctaLink?: string;
}

export interface ProductCardProps {
  id: string;
  title: string;
  price: string;
  image: string;
  currency?: string;
  onAddToCart?: () => void;
}

export interface ProductGridProps {
  id: string;
  title?: string;
  products?: Array<{
    id: string;
    title: string;
    price: string;
    image: string;
  }>;
  columns?: number;
}

export interface CTAProps {
  id: string;
  title: string;
  subtitle?: string;
  buttonText?: string;
  buttonLink?: string;
}

// ============================================
// GENRE DEFINITIONS (Visual Styles - from Drafting Site)
// ============================================

export const Genre = {
  GLASSMORPHISM: 0,
  BRUTALISM: 1,
  NEUMORPHISM: 2,
  CYBERPUNK: 3,
  MINIMALIST: 4,
  MONOPRINT: 5,
  // Extended genres from frontend
  CYBER: 6,         // Cyber style (distinct from cyberpunk)
  NEOBRUTALIST: 7,
  LOUD: 8,
  BASE: 9           // Default/neutral genre
} as const;

export type Genre = typeof Genre[keyof typeof Genre];

export const GENRE_NAMES: Record<Genre, string> = {
  [Genre.GLASSMORPHISM]: 'Glassmorphism',
  [Genre.BRUTALISM]: 'Brutalism',
  [Genre.NEUMORPHISM]: 'Neumorphism',
  [Genre.CYBERPUNK]: 'Cyberpunk',
  [Genre.MINIMALIST]: 'Minimalist',
  [Genre.MONOPRINT]: 'Monoprint',
  // Extended genre names
  [Genre.CYBER]: 'Cyber',
  [Genre.NEOBRUTALIST]: 'Neobrutalism',
  [Genre.LOUD]: 'Loud',
  [Genre.BASE]: 'Base'
};

export const GENRE_CSS_CLASSES: Record<Genre, string> = {
  [Genre.GLASSMORPHISM]: 'genre-glassmorphism',
  [Genre.BRUTALISM]: 'genre-brutalism',
  [Genre.NEUMORPHISM]: 'genre-neumorphism',
  [Genre.CYBERPUNK]: 'genre-cyberpunk',
  [Genre.MINIMALIST]: 'genre-minimalist',
  [Genre.MONOPRINT]: 'genre-monoprint',
  // Extended genre CSS classes
  [Genre.CYBER]: 'genre-cyber',
  [Genre.NEOBRUTALIST]: 'genre-neobrutalist',
  [Genre.LOUD]: 'genre-loud',
  [Genre.BASE]: 'genre-base'
};

// ============================================
// BENTO TYPE DEFINITIONS (Grid Sizes)
// ============================================

export const BentoType = {
  HERO: 0,    // 2x2 grid units - Large featured
  WIDE: 1,    // 2x1 grid units - Horizontal
  TALL: 2,    // 1x2 grid units - Vertical  
  SMALL: 3    // 1x1 grid unit - Compact
} as const;

export type BentoType = typeof BentoType[keyof typeof BentoType];

export const BENTO_TYPE_NAMES: Record<BentoType, string> = {
  [BentoType.HERO]: 'Hero',
  [BentoType.WIDE]: 'Wide',
  [BentoType.TALL]: 'Tall',
  [BentoType.SMALL]: 'Small'
};

export const BENTO_CSS_CLASSES: Record<BentoType, string> = {
  [BentoType.HERO]: 'bento-hero',
  [BentoType.WIDE]: 'bento-wide',
  [BentoType.TALL]: 'bento-tall',
  [BentoType.SMALL]: 'bento-small'
};

export const BENTO_GRID_SPANS: Record<BentoType, { col: number; row: number }> = {
  [BentoType.HERO]: { col: 2, row: 2 },
  [BentoType.WIDE]: { col: 2, row: 1 },
  [BentoType.TALL]: { col: 1, row: 2 },
  [BentoType.SMALL]: { col: 1, row: 1 }
};

// ============================================
// LAYOUT TYPE DEFINITIONS (Legacy - for compatibility)
// ============================================

export const LayoutType = {
  STANDARD: 0,   // Standard Card
  COMPACT: 1,    // Compact / List
  FEATURED: 2,   // Featured / Heroic
  GALLERY: 3,    // Gallery / Visual
  TECHNICAL: 4,  // Technical / Data
  BOLD: 5        // Typographic / Bold
} as const;

export type LayoutType = typeof LayoutType[keyof typeof LayoutType];

export const LAYOUT_TYPE_NAMES: Record<LayoutType, string> = {
  [LayoutType.STANDARD]: 'Standard',
  [LayoutType.COMPACT]: 'Compact',
  [LayoutType.FEATURED]: 'Featured',
  [LayoutType.GALLERY]: 'Gallery',
  [LayoutType.TECHNICAL]: 'Technical',
  [LayoutType.BOLD]: 'Bold'
};

// ============================================
// VARIATION TYPE
// ============================================

export type Variation = 0 | 1 | 2;

// ============================================
// MODULE METADATA & TAGGING
// ============================================

export interface ModuleTag {
  genre: Genre;
  genreName: string;
  bentoType: BentoType;
  bentoTypeName: string;
  variation: Variation;
  isLoud: boolean;
}

export interface ModuleMetadata {
  id: number;
  tag: ModuleTag;
  cssClass: string;
  semanticId: string;
}

// ============================================
// PRODUCT DATA
// ============================================

export interface ShopifyProduct {
  id: number;
  title: string;
  description: string | null;
  vendor: string;
  price: string;
  currency: string;
  image: string | null;
  url: string;
  handle: string;
  store_domain: string;
}

export interface ProductData {
  id: string | number;
  title: string;
  description: string | null;
  price: number;
  currency: string;
  imageUrl: string | null;
  vendor: string;
  category: string;
  url?: string;
}

export interface ProductModule {
  id: string;
  templateId?: number;
  bentoType?: BentoType;
  product: ShopifyProduct;
  genre: Genre;
  semanticId?: string;
}

export interface RenderingEngineProps {
  modules: ProductModule[];
  onModuleClick?: (product: ShopifyProduct, genre: Genre) => void;
  onLoadMore?: () => void;
  hasMore?: boolean;
  isLoading?: boolean;
}

// ============================================
// LAYOUT SLOT (for grid positioning)
// ============================================

export interface LayoutSlot {
  moduleId: number;
  gridColumn?: string;
  gridRow?: string;
  priority: number;
}

export interface LayoutConfig {
  slots: LayoutSlot[];
  gridColumns: number;
  gridRows: number;
}

// ============================================
// ID ENCODING/DECODING FUNCTIONS (24-module system - 1:1 with backend)
// ============================================

// System: 6 genres × 4 bento types = 24 modules (IDs 0-23)
// This matches the backend's module ID system exactly
const MODULES_PER_GENRE = 4; // 4 bento types per genre
const BENTO_TYPES_COUNT = 4;

/**
 * Encode genre and bentoType into integer ID (0-23)
 * Formula: (genre * 4) + bentoType - matches backend exactly!
 */
export function encodeModuleId(
  genre: Genre,
  bentoType: BentoType,
  _variation: Variation = 0 // Ignored - kept for API compatibility
): number {
  return (genre * MODULES_PER_GENRE) + bentoType;
}

/**
 * Get the CSS class string for a module ID
 */
export function getModuleCssClass(id: number): string {
  const tag = decodeModuleId(id);
  const genreClass = GENRE_CSS_CLASSES[tag.genre];
  const bentoClass = BENTO_CSS_CLASSES[tag.bentoType];

  return `${genreClass} ${bentoClass}`;
}

/**
 * Generate semantic module ID
 * Format: mod-{genre}-{bentoType}-{instanceId}
 * Example: mod-glassmorphism-hero-001
 */
export function generateSemanticId(
  genre: Genre,
  bentoType: BentoType,
  instanceId: number
): string {
  const genreName = GENRE_NAMES[genre].toLowerCase();
  const bentoName = BENTO_TYPE_NAMES[bentoType].toLowerCase();
  const paddedId = String(instanceId).padStart(3, '0');

  return `mod-${genreName}-${bentoName}-${paddedId}`;
}

/**
 * Get full metadata for a module
 */
export function getModuleMetadata(id: number, instanceId?: number): ModuleMetadata {
  const tag = decodeModuleId(id);
  const semanticId = instanceId !== undefined
    ? generateSemanticId(tag.genre, tag.bentoType, instanceId)
    : generateSemanticId(tag.genre, tag.bentoType, id);

  return {
    id,
    tag,
    cssClass: getModuleCssClass(id),
    semanticId
  };
}

/**
 * Decode a module ID into its components (24-module system - 1:1 with backend)
 */
export function decodeModuleId(id: number): ModuleTag {
  const genre = Math.floor(id / MODULES_PER_GENRE) as Genre;
  const bentoType = (id % MODULES_PER_GENRE) as BentoType;

  return {
    genre,
    genreName: GENRE_NAMES[genre],
    bentoType,
    bentoTypeName: BENTO_TYPE_NAMES[bentoType],
    variation: 0, // Not used in 24-module system
    isLoud: genre === Genre.BRUTALISM,
  };
}

// ============================================
// BACKEND ID CONVERSION (24-module to 72-module)
// ============================================
// Backend uses: (genre * 4) + layout = 0-23
// Frontend uses: (genre * 12) + (bentoType * 3) + variation = 0-71

const BACKEND_MODULES_PER_GENRE = 4;

/**
 * Convert a backend module ID (0-23) to a frontend module ID (0-71).
 * This is needed because the backend's vector matching operates on 24 modules
 * while the frontend renders 72 modules (with variations).
 * 
 * @param backendId - The module ID from backend (0-23)
 * @returns Frontend-compatible module ID (0-71)
 */
export function convertBackendIdToFrontend(backendId: number): number {
  // Decode backend ID: genre = floor(id / 4), layout = id % 4
  const backendGenre = Math.floor(backendId / BACKEND_MODULES_PER_GENRE);
  const backendLayout = backendId % BACKEND_MODULES_PER_GENRE;

  // Map backend layout (0-3) to frontend bentoType
  // 0=hero, 1=wide, 2=tall, 3=small
  const bentoType = backendLayout as BentoType;

  // Encode to frontend ID using variation 0 (default)
  return encodeModuleId(backendGenre as Genre, bentoType, 0);
}

/**
 * Get the frontend-compatible ID pool for initial display (24-module system).
 * Returns IDs 0-5: one per genre (hero bento type).
 */
export function getInitialIdPool(): number[] {
  // Return IDs for one module per genre (hero type = 0)
  // These match backend's [0, 1, 2, 3, 4, 5] exactly!
  return [
    encodeModuleId(Genre.GLASSMORPHISM, BentoType.HERO),  // 0
    encodeModuleId(Genre.BRUTALISM, BentoType.HERO),      // 1
    encodeModuleId(Genre.NEUMORPHISM, BentoType.HERO),    // 2
    encodeModuleId(Genre.CYBERPUNK, BentoType.HERO),      // 3
    encodeModuleId(Genre.MINIMALIST, BentoType.HERO),     // 4
    encodeModuleId(Genre.MONOPRINT, BentoType.HERO),      // 5
  ];
}

/**
 * Get all module IDs (24 total - 1:1 with backend)
 */
export function getAllModuleIds(): number[] {
  const ids: number[] = [];
  for (let genre = 0; genre < 6; genre++) {
    for (let bentoType = 0; bentoType < BENTO_TYPES_COUNT; bentoType++) {
      ids.push(encodeModuleId(genre as Genre, bentoType as BentoType, 0));
    }
  }
  return ids;
}

/**
 * Get random module ID of a specific bento type
 */
export function getRandomModuleOfBentoType(bentoType: BentoType): number {
  const genre = Math.floor(Math.random() * 6) as Genre;
  return encodeModuleId(genre, bentoType, 0);
}

/**
 * Get all module IDs of a specific bento type (4 per bento type)
 */
export function getModulesOfBentoType(bentoType: BentoType): number[] {
  const ids: number[] = [];
  for (let genre = 0; genre < 6; genre++) {
    ids.push(encodeModuleId(genre as Genre, bentoType, 0));
  }
  return ids;
}

/**
 * Get all module IDs of a specific genre (4 per genre)
 */
export function getModulesOfGenre(genre: Genre): number[] {
  const ids: number[] = [];
  for (let bentoType = 0; bentoType < BENTO_TYPES_COUNT; bentoType++) {
    ids.push(encodeModuleId(genre, bentoType as BentoType, 0));
  }
  return ids;
}

/**
 * Legacy compatibility functions (deprecated)
 */

// Old system: 6 genres × 6 layouts = 36 modules
const LEGACY_MODULES_PER_GENRE = 6;

/**
 * @deprecated Use encodeModuleId instead
 */
export function encodeLegacyModuleId(
  genre: Genre,
  layout: LayoutType
): number {
  return (genre * LEGACY_MODULES_PER_GENRE) + layout;
}
