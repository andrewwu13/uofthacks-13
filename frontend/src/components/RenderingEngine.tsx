import React, { memo, useEffect, useRef } from 'react';
import { RenderingEngineProps } from '../schema/types'; // Updated import
import { getModuleConfig } from './modules/ModuleRegistry';

export const RenderingEngine: React.FC<RenderingEngineProps> = ({
  modules,
  onModuleClick,
  showDebugInfo = true,
  onLoadMore,
  hasMore,
  isLoading
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
  }, [loadMoreRef.current]); // Added dependency to re-run if ref changes (usually stable)

  return (
    <div className="rendering-engine">
      <div className="module-grid">
        {modules.map((module) => {
          // Use the templateId to determine layout/genre
          const templateId = module.templateId !== undefined
            ? module.templateId
            : 0; // Fallback

          const config = getModuleConfig(templateId);
          const LayoutComponent = config.component;

          // Map backend product data to props
          // Note: ShopifyProduct properties are strings/numbers, ProductData expects specific types
          const productData = {
            id: module.product.id,
            title: module.product.title,
            description: module.product.description,
            price: parseFloat(module.product.price),
            currency: module.product.currency,
            imageUrl: module.product.image,
            vendor: module.product.vendor,
            category: 'General', // Fallback
            url: module.product.url
          };

          return (
            <div
              key={`${module.id}-${templateId}`}
              className={`module-wrapper ${config.className}`}
            >
              <LayoutComponent
                product={productData}
                genre={config.genre}
                showDebug={showDebugInfo}
                onAddToCart={() => {
                  if (onModuleClick) {
                    onModuleClick(module.product, config.genre);
                  }
                }}
              />
            </div>
          );
        })}
      </div>

      {/* Infinite scroll trigger */}
      <div ref={loadMoreRef} className="load-more-trigger">
        {isLoading && (
          <div className="loading-indicator">
            <div className="loading-spinner"></div>
            <span>Loading more products...</span>
          </div>
        )}
        {!hasMore && (
          <div className="end-message">End of catalog</div>
        )}
      </div>
    </div>
  );
};

export default RenderingEngine;