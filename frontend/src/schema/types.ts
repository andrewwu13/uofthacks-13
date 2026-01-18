/**
 * Gen UI Schema Types
 * 
 * Module ID System:
 * Each module has a unique ID that encodes:
 * - Genre (0-5): The visual style
 * - ModuleType (0-5): The functional component type
 * - Variation (0-2): Style variation within genre/type combo
 * 
 * ID = (genre * 18) + (moduleType * 3) + variation
 * This gives us 6 × 6 × 3 = 108 unique module templates
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
// GENRE DEFINITIONS (Visual Styles)
// ============================================

export const Genre = {
  BASE: 0,
  MINIMALIST: 1,
  NEOBRUTALIST: 2,
  GLASSMORPHISM: 3,
  LOUD: 4,
  CYBER: 5
} as const;

export type Genre = typeof Genre[keyof typeof Genre];

export const GENRE_NAMES: Record<Genre, string> = {
  [Genre.BASE]: 'Base',
  [Genre.MINIMALIST]: 'Minimalist',
  [Genre.NEOBRUTALIST]: 'Neobrutalist',
  [Genre.GLASSMORPHISM]: 'Glassmorphism',
  [Genre.LOUD]: 'Loud',
  [Genre.CYBER]: 'Cyber'
};

export const GENRE_CSS_CLASSES: Record<Genre, string> = {
  [Genre.BASE]: 'genre-base',
  [Genre.MINIMALIST]: 'genre-minimalist',
  [Genre.NEOBRUTALIST]: 'genre-neobrutalist',
  [Genre.GLASSMORPHISM]: 'genre-glassmorphism',
  [Genre.LOUD]: 'genre-loud',
  [Genre.CYBER]: 'genre-cyber'
};

// ============================================
// LAYOUT TYPE DEFINITIONS (Functional Components)
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
  layout: LayoutType;
  layoutName: string;
  isLoud: boolean;
}

export interface ModuleMetadata {
  id: number;
  tag: ModuleTag;
  cssClass: string;
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
  product: ShopifyProduct;
  genre: Genre;
}

export interface RenderingEngineProps {
  modules: ProductModule[];
  onModuleClick?: (product: ShopifyProduct, genre: Genre) => void;
  showDebugInfo?: boolean;
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
// ID ENCODING/DECODING FUNCTIONS
// ============================================


// ============================================
// ID ENCODING/DECODING FUNCTIONS (0-35 System)
// ============================================

const MODULES_PER_GENRE = 6;

/**
 * Encode genre and layout into integer ID (0-35)
 */
export function encodeModuleId(
  genre: Genre,
  layout: LayoutType
): number {
  return (genre * MODULES_PER_GENRE) + layout;
}

/**
 * Get the CSS class string for a module ID
 */
export function getModuleCssClass(id: number): string {
  const tag = decodeModuleId(id);
  const genreClass = GENRE_CSS_CLASSES[tag.genre];
  const layoutClass = `layout-${LAYOUT_TYPE_NAMES[tag.layout].toLowerCase()}`;

  return `${genreClass} ${layoutClass}`;
}

/**
 * Get full metadata for a module
 */
export function getModuleMetadata(id: number): ModuleMetadata {
  return {
    id,
    tag: decodeModuleId(id),
    cssClass: getModuleCssClass(id)
  };
}

/**
 * Decode a module ID into its components
 */
export function decodeModuleId(id: number): ModuleTag {
  const genre = (Math.floor(id / MODULES_PER_GENRE) % 6) as Genre;
  const layout = (id % MODULES_PER_GENRE) as LayoutType;

  return {
    genre,
    genreName: GENRE_NAMES[genre],
    layout,
    layoutName: LAYOUT_TYPE_NAMES[layout],
    isLoud: genre === Genre.LOUD,
  };
}

/**
 * Get all module IDs (36 total)
 */
export function getAllModuleIds(): number[] {
  const ids: number[] = [];
  for (let genre = 0; genre < 6; genre++) {
    for (let layout = 0; layout < 6; layout++) {
      ids.push(encodeModuleId(genre as Genre, layout as LayoutType));
    }
  }
  return ids;
}

/**
 * Get random module ID of a specific layout (for replacement)
 */
export function getRandomModuleOfLayout(layout: LayoutType): number {
  const genre = Math.floor(Math.random() * 6) as Genre;
  return encodeModuleId(genre, layout);
}

/**
 * Get all module IDs of a specific layout
 */
export function getModulesOfLayout(layout: LayoutType): number[] {
  const ids: number[] = [];
  for (let genre = 0; genre < 6; genre++) {
    ids.push(encodeModuleId(genre as Genre, layout));
  }
  return ids;
}

/**
 * Get all module IDs of a specific genre
 */
export function getModulesOfGenre(genre: Genre): number[] {
  const ids: number[] = [];
  for (let layout = 0; layout < 6; layout++) {
    ids.push(encodeModuleId(genre, layout as LayoutType));
  }
  return ids;
}
