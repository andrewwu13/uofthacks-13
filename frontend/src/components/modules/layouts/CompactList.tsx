import React from 'react';
import { GENRE_NAMES } from '../../../schema/types';
import type { LayoutProps } from './types';

export const CompactList: React.FC<LayoutProps> = ({
    product,
    genre,
    onAddToCart,
    className = '',
    showDebug
}) => {
    const price = parseFloat(product.price.toString()) || 0;

    return (
        <div
            className={`module-card module-layout-compact ${className}`}
            data-genre={GENRE_NAMES[genre]}
        >
            <div className="compact-row">
                {/* Left: Image */}
                <div className="compact-image-container">
                    {product.imageUrl ? (
                        <img
                            src={product.imageUrl}
                            alt={product.title}
                            className="product-image"
                            loading="lazy"
                        />
                    ) : (
                        <div className="product-image-placeholder">No Image</div>
                    )}
                </div>

                {/* Right: Content */}
                <div className="compact-content">
                    <div className="compact-header">
                        <h3 className="product-title">{product.title}</h3>
                        <span className="product-vendor">{product.vendor}</span>
                    </div>

                    <div className="compact-footer">
                        <span className="price-amount">${price.toFixed(2)}</span>
                        <button
                            className="module-btn compact-btn"
                            onClick={(e) => {
                                e.stopPropagation();
                                onAddToCart?.();
                                if (product.url) {
                                    window.open(product.url, '_blank');
                                }
                            }}
                        >
                            Add
                        </button>
                    </div>
                </div>
            </div>

            {showDebug && (
                <div className="debug-overlay">
                    {GENRE_NAMES[genre]} / Compact
                </div>
            )}
        </div>
    );
};
