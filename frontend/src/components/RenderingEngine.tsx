/**
 * Gen UI Rendering Engine - Product Focused
 * 
 * This engine displays real Shopify products with different visual genres.
 * Each module shows a real product scraped from Shopify stores.
 * 
 * Genre (visual style): 0-5
 *   0 = Base (clean dark UI)
 *   1 = Minimalist (stark, Swiss-inspired)
 *   2 = Neobrutalist (bold, raw, playful)
 *   3 = Glassmorphism (translucent, dreamy)
 *   4 = Loud (gradient, energetic)
 *   5 = Cyber (matrix, terminal aesthetic)
 */

import React, { memo, useEffect, useRef, useCallback } from 'react';
import {
  Genre,
  GENRE_NAMES,
} from '../schema/types';
import type { ShopifyProduct } from '../api/products';

// ============================================
// TYPES
// ============================================

// Module with real product data
export interface ProductModule {
  id: string;          // Unique identifier for this module instance
  product: ShopifyProduct;  // Real product data from API
  genre: Genre;        // Visual style (0-5)
  templateId?: number; // Integer ID (0-35) driving the style
}

interface RenderingEngineProps {
  modules: ProductModule[];
  onModuleClick?: (product: ShopifyProduct, genre: Genre) => void;
  showDebugInfo?: boolean;
  onLoadMore?: () => void;
  isLoading?: boolean;
}

// ============================================
// DEBUG OVERLAY COMPONENT (Memoized)
// ============================================

interface DebugOverlayProps {
  product: ShopifyProduct;
  genre: Genre;
}

const DebugOverlay = memo<DebugOverlayProps>(({ product, genre }) => (
  <div className="module-debug-overlay">
    <div className="debug-id">ID: {product.id}</div>
    <div className="debug-genre">{GENRE_NAMES[genre]}</div>
    <div className="debug-type">{product.store_domain}</div>
  </div>
));

DebugOverlay.displayName = 'DebugOverlay';

// ============================================
// GENRE CSS CLASSES
// ============================================

const GENRE_CLASSES: Record<Genre, string> = {
  [Genre.BASE]: 'genre-base',
  [Genre.MINIMALIST]: 'genre-minimalist',
  [Genre.NEOBRUTALIST]: 'genre-neobrutalist',
  [Genre.GLASSMORPHISM]: 'genre-glassmorphism',
  [Genre.LOUD]: 'genre-loud',
  [Genre.CYBER]: 'genre-cyber'
};

// ============================================
// PRODUCT CARD COMPONENT (Memoized)
// ============================================

interface ProductCardProps {
  module: ProductModule;
  onModuleClick?: (product: ShopifyProduct, genre: Genre) => void;
  showDebugInfo: boolean;
}

import { decodeModuleId } from '../schema/types';

const ProductCard = memo<ProductCardProps>(({ module, onModuleClick, showDebugInfo }) => {
  const { product, genre: fallbackGenre, templateId } = module;

  // If templateId exists, derive genre from it. Otherwise use fallback.
  const effectiveGenre = templateId !== undefined
    ? decodeModuleId(templateId).genre
    : fallbackGenre;

  const genreClass = GENRE_CLASSES[effectiveGenre];

  const handleClick = useCallback(() => {
    if (onModuleClick) {
      onModuleClick(product, genre);
    }
  }, [product, genre, onModuleClick]);

  // Get button text based on genre
  const getButtonText = () => {
    switch (genre) {
      case Genre.NEOBRUTALIST: return 'BUY NOW';
      case Genre.LOUD: return 'ADD TO CART 🔥';
      case Genre.CYBER: return '>> ACQUIRE';
      case Genre.MINIMALIST: return 'Add';
      default: return 'Add to Cart';
    }
  };

  // Get badge based on genre
  const getBadge = () => {
    if (genre === Genre.LOUD) return { text: 'HOT', show: true };
    if (genre === Genre.NEOBRUTALIST) return { text: 'NEW', show: true };
    if (genre === Genre.CYBER) return { text: 'LIVE', show: true };
    return { text: '', show: false };
  };

  const badge = getBadge();
  const price = parseFloat(product.price) || 0;

  return (
    <div
      onClick={handleClick}
      className="module-wrapper"
      data-module-id={module.id}
      data-track-id={`product_${product.id}`}
    >
      {showDebugInfo && <DebugOverlay product={product} genre={genre} />}

      <div className={`module-card module-product-card ${genreClass}`} data-genre={GENRE_NAMES[genre]}>
        {/* Badge */}
        {badge.show && (
          <div className="module-badge">{badge.text}</div>
        )}

        {/* Product Image */}
        <div className="product-image-container">
          {product.image ? (
            <img
              src={product.image}
              alt={product.title}
              className="product-image"
              loading="lazy"
            />
          ) : (
            <div className="product-image-placeholder">No Image</div>
          )}
        </div>

        {/* Product Info */}
        <div className="product-info">
          <span className="product-vendor">{product.vendor}</span>
          <h3 className="product-title" data-track-id={`${product.id}_title`}>{product.title}</h3>
          {product.description && (
            <p className="product-description">{product.description}</p>
          )}
          <div
            className="product-price"
            data-track-context="price"
            data-track-id={`${product.id}_price`}
          >
            <span className="price-currency">{product.currency}</span>
            <span className="price-amount">${price.toFixed(2)}</span>
          </div>
          <div className="product-store">
            <span className="store-domain">from {product.store_domain}</span>
          </div>
        </div>

        {/* Action Button */}
        <a
          href={product.url}
          target="_blank"
          rel="noopener noreferrer"
          className="module-btn"
          data-track-id={`${product.id}_add_cart`}
          onClick={(e) => e.stopPropagation()}
        >
          {getButtonText()}
        </a>
      </div>
    </div>
  );
});

ProductCard.displayName = 'ProductCard';

// ============================================
// RENDERING ENGINE COMPONENT
// ============================================

export const RenderingEngine: React.FC<RenderingEngineProps> = ({
  modules,
  onModuleClick,
  showDebugInfo = true,
  onLoadMore,
  isLoading = false
}) => {
  const loadMoreRef = useRef<HTMLDivElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  // Stable callback ref for onLoadMore
  const onLoadMoreRef = useRef(onLoadMore);
  onLoadMoreRef.current = onLoadMore;

  // Intersection Observer for infinite scroll
  useEffect(() => {
    if (!loadMoreRef.current) return;

    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    observerRef.current = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting && onLoadMoreRef.current) {
          onLoadMoreRef.current();
        }
      },
      {
        root: null,
        rootMargin: '400px',
        threshold: 0.1
      }
    );

    observerRef.current.observe(loadMoreRef.current);

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, []);

  return (
    <div className="rendering-engine">
      <div className="module-grid">
        {modules.map((module) => (
          <ProductCard
            key={module.id}
            module={module}
            onModuleClick={onModuleClick}
            showDebugInfo={showDebugInfo}
          />
        ))}
      </div>

      {/* Infinite scroll trigger */}
      <div ref={loadMoreRef} className="load-more-trigger">
        {isLoading && (
          <div className="loading-indicator">
            <div className="loading-spinner"></div>
            <span>Loading more products...</span>
          </div>
        )}
      </div>
    </div>
  );
};

// ============================================
// UTILITY: Create Product Modules
// ============================================

let moduleCounter = 0;

/**
 * Create product modules from API data with minimal genre (baseline for profile evolution)
 */
export function createProductModules(products: ShopifyProduct[]): ProductModule[] {
  return products.map((product) => {
    moduleCounter++;
    // Start with MINIMALIST genre as neutral baseline
    const genre = Genre.MINIMALIST;

    return {
      id: `product-${moduleCounter}-${product.id}`,
      product,
      genre
    };
  });
}

/**
 * Create a batch of product modules for infinite scroll
 * Samples templateId from the provided random pool.
 */
export function createProductBatch(
  allProducts: ShopifyProduct[],
  currentCount: number,
  batchSize: number = 3,
  idPool: number[] = [0] // Default pool if not provided
): ProductModule[] {
  const modules: ProductModule[] = [];

  for (let i = 0; i < batchSize; i++) {
    // Cycle through products if we run out
    const productIndex = (currentCount + i) % allProducts.length;
    const product = allProducts[productIndex];

    // Sample a Template ID from the pool
    const randomPoolIndex = Math.floor(Math.random() * idPool.length);
    const templateId = idPool[randomPoolIndex];

    // Fallback genre (derived or default)
    const genre = Genre.MINIMALIST;

    moduleCounter++;
    modules.push({
      id: `product-${moduleCounter}-${product.id}-${Date.now()}-${i}`,
      product,
      genre,     // Kept for fallback types
      templateId // The driver of the new style
    });
  }

  return modules;
}

export default RenderingEngine;