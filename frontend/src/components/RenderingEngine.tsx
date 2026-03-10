import React, { useEffect, useRef, useCallback } from 'react';
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

  // Stable refs — always reflect latest values without re-subscribing
  const onLoadMoreRef = useRef(onLoadMore);
  onLoadMoreRef.current = onLoadMore;
  const hasMoreRef = useRef(hasMore);
  hasMoreRef.current = hasMore;
  const isLoadingRef = useRef(isLoading);
  isLoadingRef.current = isLoading;

  // Use a scroll event on the window for maximum reliability.
  // IntersectionObserver requires the trigger element to LEAVE the
  // extended zone before it can re-fire — which doesn't happen when
  // new content pushes it down while you're still scrolling.
  const checkScroll = useCallback(() => {
    if (isLoadingRef.current || !hasMoreRef.current) return;
    if (!loadMoreRef.current) return;

    const rect = loadMoreRef.current.getBoundingClientRect();
    const triggerDistance = window.innerHeight + 800; // Load when within 800px

    if (rect.top <= triggerDistance) {
      onLoadMoreRef.current?.();
    }
  }, []);

  useEffect(() => {
    window.addEventListener('scroll', checkScroll, { passive: true });
    // Also fire immediately in case the user is already near the bottom
    // (e.g. after new modules load and the trigger is still in range)
    checkScroll();

    return () => {
      window.removeEventListener('scroll', checkScroll);
    };
  }, [checkScroll, modules.length]); // Re-register after each batch so checkScroll fires immediately

  return (
    <div className="rendering-engine">
      <div className="bento-grid">
        {modules.map((module, index) => {
          const templateId = module.templateId !== undefined ? module.templateId : 0;
          const bentoType = module.bentoType !== undefined ? module.bentoType : 0;

          const config = getModuleConfig(templateId);
          const LayoutComponent = config.component;

          const gridSpan = BENTO_GRID_SPANS[bentoType as BentoType] || BENTO_GRID_SPANS[0];
          const semanticId = module.semanticId || generateSemanticId(
            config.genre,
            bentoType as BentoType,
            index + 1
          );

          const productData = {
            id: module.product.id,
            title: module.product.title,
            description: module.product.description,
            price: parseFloat(module.product.price),
            currency: module.product.currency,
            imageUrl: module.product.image,
            vendor: module.product.vendor,
            category: 'General',
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

      {/* Scroll anchor — used for position measurement */}
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