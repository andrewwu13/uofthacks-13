/**
 * Gen UI Rendering Engine
 * 
 * This engine takes an array of module IDs and builds the storefront page.
 * Each module ID encodes:
 * - Genre (visual style): 0-5
 * - Module Type (component): 0-5
 * - Variation (size/layout): 0-2
 * 
 * The engine:
 * 1. Decodes each module ID
 * 2. Selects the appropriate component
 * 3. Applies the genre styling
 * 4. Renders in a 2x3 grid layout
 */

import React, { useMemo } from 'react';
import {
  decodeModuleId,
  ModuleType,
  Genre,
  Variation,
  encodeModuleId
} from '../schema/types';
import type { ModuleTag } from '../schema/types';
import {
  getRandomHero,
  getRandomBanner,
  getRandomFeatures,
  getRandomTestimonial,
  getRandomCTA,
  PRODUCTS
} from '../schema/data';

// Import all modules
import { ProductCard } from '../modules/ProductCard';
import { Hero } from '../modules/Hero';
import { Banner } from '../modules/Banner';
import { FeatureList } from '../modules/FeatureList';
import { Testimonial } from '../modules/Testimonial';
import { CTA } from '../modules/CTA';

// ============================================
// TYPES
// ============================================

interface RenderingEngineProps {
  moduleIds: number[];
  onModuleClick?: (moduleId: number, tag: ModuleTag) => void;
}

// ============================================
// MODULE RENDERER
// ============================================

/**
 * Renders a single module based on its ID
 */
const renderModule = (
  moduleId: number,
  index: number,
  onModuleClick?: (moduleId: number, tag: ModuleTag) => void
): React.ReactNode => {
  const tag = decodeModuleId(moduleId);
  const { genre, moduleType, variation } = tag;
  const key = `module-${moduleId}-${index}`;

  // Wrapper for click handling
  const handleClick = () => {
    if (onModuleClick) {
      onModuleClick(moduleId, tag);
    }
  };

  // Render the appropriate component with properly typed content
  switch (moduleType) {
    case ModuleType.PRODUCT_CARD: {
      const product = PRODUCTS[index % PRODUCTS.length];
      return (
        <div key={key} onClick={handleClick} className="module-wrapper">
          <ProductCard
            genre={genre}
            variation={variation}
            product={product}
            moduleId={moduleId}
          />
        </div>
      );
    }

    case ModuleType.HERO: {
      const content = getRandomHero();
      return (
        <div key={key} onClick={handleClick} className="module-wrapper">
          <Hero
            genre={genre}
            variation={variation}
            content={content}
            moduleId={moduleId}
          />
        </div>
      );
    }

    case ModuleType.BANNER: {
      const content = getRandomBanner();
      return (
        <div key={key} onClick={handleClick} className="module-wrapper">
          <Banner
            genre={genre}
            variation={variation}
            content={content}
            moduleId={moduleId}
          />
        </div>
      );
    }

    case ModuleType.FEATURE_LIST: {
      const features = getRandomFeatures();
      return (
        <div key={key} onClick={handleClick} className="module-wrapper">
          <FeatureList
            genre={genre}
            variation={variation}
            features={features}
            moduleId={moduleId}
          />
        </div>
      );
    }

    case ModuleType.TESTIMONIAL: {
      const content = getRandomTestimonial();
      return (
        <div key={key} onClick={handleClick} className="module-wrapper">
          <Testimonial
            genre={genre}
            variation={variation}
            content={content}
            moduleId={moduleId}
          />
        </div>
      );
    }

    case ModuleType.CTA: {
      const content = getRandomCTA();
      return (
        <div key={key} onClick={handleClick} className="module-wrapper">
          <CTA
            genre={genre}
            variation={variation}
            content={content}
            moduleId={moduleId}
          />
        </div>
      );
    }

    default:
      return (
        <div key={key} className="module-wrapper module-unknown">
          Unknown Module Type: {moduleType}
        </div>
      );
  }
};

// ============================================
// RENDERING ENGINE COMPONENT
// ============================================

export const RenderingEngine: React.FC<RenderingEngineProps> = ({
  moduleIds,
  onModuleClick
}) => {
  // Memoize rendered modules to prevent unnecessary re-renders
  const renderedModules = useMemo(() => {
    return moduleIds.map((id, index) => renderModule(id, index, onModuleClick));
  }, [moduleIds, onModuleClick]);

  return (
    <div className="rendering-engine">
      <div className="module-grid">
        {renderedModules}
      </div>
    </div>
  );
};

// ============================================
// UTILITY: Generate Random Layout
// ============================================

/**
 * Generate a random set of module IDs for the storefront
 * Ensures variety by picking different types and genres
 */
export function generateRandomLayout(count: number = 6): number[] {
  const ids: number[] = [];

  // For a 6-slot layout, we want variety
  // Let's pick different module types and genres
  for (let i = 0; i < count; i++) {
    const genre = Math.floor(Math.random() * 6) as Genre;
    const moduleType = i % 6 as ModuleType; // Cycle through types
    const variation = Math.floor(Math.random() * 3) as Variation;

    ids.push(encodeModuleId(genre, moduleType, variation));
  }

  return ids;
}

/**
 * Generate a layout with all product cards (different genres)
 */
export function generateProductShowcase(): number[] {
  return [
    encodeModuleId(Genre.BASE, ModuleType.PRODUCT_CARD, Variation.DEFAULT),
    encodeModuleId(Genre.MINIMALIST, ModuleType.PRODUCT_CARD, Variation.DEFAULT),
    encodeModuleId(Genre.NEOBRUTALIST, ModuleType.PRODUCT_CARD, Variation.DEFAULT),
    encodeModuleId(Genre.GLASSMORPHISM, ModuleType.PRODUCT_CARD, Variation.DEFAULT),
    encodeModuleId(Genre.LOUD, ModuleType.PRODUCT_CARD, Variation.DEFAULT),
    encodeModuleId(Genre.CYBER, ModuleType.PRODUCT_CARD, Variation.DEFAULT),
  ];
}

/**
 * Generate a mixed storefront layout
 */
export function generateStorefrontLayout(): number[] {
  return [
    encodeModuleId(Genre.BASE, ModuleType.HERO, Variation.DEFAULT),
    encodeModuleId(Genre.MINIMALIST, ModuleType.PRODUCT_CARD, Variation.DEFAULT),
    encodeModuleId(Genre.NEOBRUTALIST, ModuleType.BANNER, Variation.DEFAULT),
    encodeModuleId(Genre.GLASSMORPHISM, ModuleType.FEATURE_LIST, Variation.DEFAULT),
    encodeModuleId(Genre.LOUD, ModuleType.CTA, Variation.DEFAULT),
    encodeModuleId(Genre.CYBER, ModuleType.TESTIMONIAL, Variation.DEFAULT),
  ];
}

/**
 * Replace a module at a specific index with a new one of the same type
 * but different genre/variation
 */
export function replaceModule(
  currentIds: number[],
  index: number,
  newGenre?: Genre,
  newVariation?: Variation
): number[] {
  const newIds = [...currentIds];
  const currentTag = decodeModuleId(currentIds[index]);

  // Keep the same module type, but change genre/variation
  const genre = newGenre ?? (Math.floor(Math.random() * 6) as Genre);
  const variation = newVariation ?? (Math.floor(Math.random() * 3) as Variation);

  newIds[index] = encodeModuleId(genre, currentTag.moduleType, variation);

  return newIds;
}

export default RenderingEngine;