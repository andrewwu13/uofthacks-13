import React, { useEffect, useRef } from 'react';
import type { RenderingEngineProps, BentoType } from '../schema/types';
import { getModuleConfig } from './modules/ModuleRegistry';
import { BENTO_GRID_SPANS, generateSemanticId } from '../schema/types';

export const RenderingEngine: React.FC<RenderingEngineProps> = ({
  modules,
  onModuleClick,
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
  }, [loadMoreRef.current]);

  return (
    <div className="rendering-engine">
      <div className="bento-grid">
        {modules.map((module, index) => {
          // Use the templateId to determine bento type/genre
          const templateId = module.templateId !== undefined
            ? module.templateId
            : 0; // Fallback

          // Get bento type from module or default to small
          const bentoType = module.bentoType !== undefined
            ? module.bentoType
            : 0; // Default to BentoType.HERO

          const config = getModuleConfig(templateId);
          const LayoutComponent = config.component;

          // Calculate grid span based on bento type
          const gridSpan = BENTO_GRID_SPANS[bentoType as BentoType] || BENTO_GRID_SPANS[0];

          // Generate semantic ID for this specific module instance
          const semanticId = module.semanticId || generateSemanticId(
            config.genre,
            bentoType as BentoType,
            index + 1
          );

          // Map backend product data to props
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
              key={`${module.id}-${templateId}-${index}`}
              className={`module-wrapper bento-item-wrapper ${config.className}`}
              data-template-id={templateId}
              data-bento-type={bentoType}
              data-semantic-id={semanticId}
              data-module-index={index}
              style={{
                '--bento-col-span': gridSpan.col,
                '--bento-row-span': gridSpan.row
              } as React.CSSProperties}
            >
              <LayoutComponent
                product={productData}
                genre={config.genre}
                bentoType={bentoType as BentoType}
                moduleId={String(templateId)}
                semanticId={semanticId}
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