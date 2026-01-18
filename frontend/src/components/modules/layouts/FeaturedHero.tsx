import React from 'react';
import { GENRE_NAMES } from '../../../schema/types';
import type { LayoutProps } from './types';

export const FeaturedHero: React.FC<LayoutProps> = ({
    product,
    genre,
    onAddToCart,
    className = '',
    showDebug
}) => {
    return (
        <div
            className={`module-card module-layout-featured ${className}`}
            data-genre={GENRE_NAMES[genre]}
            style={{ backgroundImage: `url(${product.imageUrl})` }}
        >
            <div className="featured-overlay">
                <div className="featured-content">
                    <span className="featured-label">Featured Drop</span>
                    <h2 className="product-title">{product.title}</h2>
                    <p className="product-price">${product.price}</p>

                    <button
                        className="module-btn featured-btn"
                        onClick={(e) => {
                            e.stopPropagation();
                            onAddToCart?.();
                        }}
                    >
                        Shop Now
                    </button>
                </div>
            </div>

            {showDebug && <div className="debug-overlay">Featured / {GENRE_NAMES[genre]}</div>}
        </div>
    );
};
