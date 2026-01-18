import React from 'react';
import type { ProductData, Genre } from '../../../schema/types';
import { GENRE_NAMES } from '../../../schema/types';

export interface LayoutProps {
    product: ProductData;
    genre: Genre;
    onAddToCart?: () => void;
    className?: string;
    showDebug?: boolean;
}

export const StandardCard: React.FC<LayoutProps> = ({
    product,
    genre,
    onAddToCart,
    className = '',
    showDebug
}) => {
    const price = parseFloat(product.price.toString()) || 0;

    return (
        <div
            className={`module-card module-layout-standard ${className}`}
            data-genre={GENRE_NAMES[genre]}
        >
            {/* Product Image */}
            <div className="product-image-container">
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

            {/* Product Info */}
            <div className="product-info">
                <span className="product-vendor">{product.vendor}</span>
                <h3 className="product-title">{product.title}</h3>

                {product.description && (
                    <p className="product-description">{product.description}</p>
                )}

                <div className="product-price">
                    <span className="price-currency">{product.currency}</span>
                    <span className="price-amount">${price.toFixed(2)}</span>
                </div>
            </div>

            {/* Action Button */}
            <button
                className="module-btn"
                onClick={(e) => {
                    e.stopPropagation();
                    onAddToCart?.();
                }}
            >
                Add to Cart
            </button>

            {showDebug && (
                <div className="debug-overlay">
                    ID: {product.id} | {GENRE_NAMES[genre]}
                </div>
            )}
        </div>
    );
};
