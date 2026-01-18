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
// MODULE TYPE DEFINITIONS (Functional Components)
// ============================================

export const ModuleType = {
  PRODUCT_CARD: 0,
  HERO: 1,
  BANNER: 2,
  FEATURE_LIST: 3,
  TESTIMONIAL: 4,
  CTA: 5
} as const;

export type ModuleType = typeof ModuleType[keyof typeof ModuleType];

export const MODULE_TYPE_NAMES: Record<ModuleType, string> = {
  [ModuleType.PRODUCT_CARD]: 'ProductCard',
  [ModuleType.HERO]: 'Hero',
  [ModuleType.BANNER]: 'Banner',
  [ModuleType.FEATURE_LIST]: 'FeatureList',
  [ModuleType.TESTIMONIAL]: 'Testimonial',
  [ModuleType.CTA]: 'CTA'
};

// ============================================
// VARIATION DEFINITIONS
// ============================================

export const Variation = {
  DEFAULT: 0,
  COMPACT: 1,
  EXPANDED: 2
} as const;

export type Variation = typeof Variation[keyof typeof Variation];

// ============================================
// MODULE METADATA & TAGGING
// ============================================

export interface ModuleTag {
  genre: Genre;
  genreName: string;
  moduleType: ModuleType;
  moduleTypeName: string;
  variation: Variation;
  isLoud: boolean;
  canReplace: ModuleType;
}

export interface ModuleMetadata {
  id: number;
  tag: ModuleTag;
  cssClass: string;
}

// ============================================
// PRODUCT DATA
// ============================================

export interface ProductData {
  id: string;
  title: string;
  description: string;
  price: number;
  currency: string;
  imageUrl: string;
  vendor: string;
  category: string;
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

const MODULES_PER_GENRE = 18;  // 6 types × 3 variations
const VARIATIONS_PER_TYPE = 3;

/**
 * Encode genre, moduleType, variation into a single module ID
 */
export function encodeModuleId(
  genre: Genre,
  moduleType: ModuleType,
  variation: Variation = Variation.DEFAULT
): number {
  return (genre * MODULES_PER_GENRE) + (moduleType * VARIATIONS_PER_TYPE) + variation;
}

/**
 * Decode a module ID into its components
 */
export function decodeModuleId(id: number): ModuleTag {
  const genre = (Math.floor(id / MODULES_PER_GENRE) % 6) as Genre;
  const remainder = id % MODULES_PER_GENRE;
  const moduleType = Math.floor(remainder / VARIATIONS_PER_TYPE) as ModuleType;
  const variation = (remainder % VARIATIONS_PER_TYPE) as Variation;

  return {
    genre,
    genreName: GENRE_NAMES[genre],
    moduleType,
    moduleTypeName: MODULE_TYPE_NAMES[moduleType],
    variation,
    isLoud: genre === Genre.LOUD,
    canReplace: moduleType
  };
}

/**
 * Get the CSS class string for a module ID
 */
export function getModuleCssClass(id: number): string {
  const tag = decodeModuleId(id);
  const genreClass = GENRE_CSS_CLASSES[tag.genre];
  const typeClass = `module-${MODULE_TYPE_NAMES[tag.moduleType].toLowerCase()}`;
  const variationClass = `variation-${tag.variation}`;

  return `${genreClass} ${typeClass} ${variationClass}`;
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
 * Generate all possible module IDs (108 total)
 */
export function getAllModuleIds(): number[] {
  const ids: number[] = [];
  for (let genre = 0; genre < 6; genre++) {
    for (let moduleType = 0; moduleType < 6; moduleType++) {
      for (let variation = 0; variation < 3; variation++) {
        ids.push(encodeModuleId(genre as Genre, moduleType as ModuleType, variation as Variation));
      }
    }
  }
  return ids;
}

/**
 * Get random module ID of a specific type (for replacement)
 */
export function getRandomModuleOfType(moduleType: ModuleType): number {
  const genre = Math.floor(Math.random() * 6) as Genre;
  const variation = Math.floor(Math.random() * 3) as Variation;
  return encodeModuleId(genre, moduleType, variation);
}

/**
 * Get all module IDs of a specific type
 */
export function getModulesOfType(moduleType: ModuleType): number[] {
  const ids: number[] = [];
  for (let genre = 0; genre < 6; genre++) {
    for (let variation = 0; variation < 3; variation++) {
      ids.push(encodeModuleId(genre as Genre, moduleType as ModuleType, variation as Variation));
    }
  }
  return ids;
}

/**
 * Get all module IDs of a specific genre
 */
export function getModulesOfGenre(genre: Genre): number[] {
  const ids: number[] = [];
  for (let moduleType = 0; moduleType < 6; moduleType++) {
    for (let variation = 0; variation < 3; variation++) {
      ids.push(encodeModuleId(genre, moduleType as ModuleType, variation as Variation));
    }
  }
  return ids;
}
