import React from 'react';
import { GENRE_NAMES } from '../../../schema/types';
import type { LayoutProps } from './types';

export const GalleryView: React.FC<LayoutProps> = ({
    product,
    genre,
    onAddToCart,
    className = '',
    showDebug
}) => {
    return (
        <div
            className={`module-card module-layout-gallery ${className}`}
            data-genre={GENRE_NAMES[genre]}
        >
            <div className="gallery-image-wrapper">
                <img
                    src={product.imageUrl || ''}
                    alt={product.title}
                    className="product-image"
                    loading="lazy"
                />

                {/* Helper overlay that appears on hover */}
                <div className="gallery-hover-info">
                    <h3 className="product-title">{product.title}</h3>
                    <span className="product-price">${product.price}</span>
                    <button
                        className="gallery-add-btn"
                        onClick={(e) => {
                            e.stopPropagation();
                            onAddToCart?.();
                            if (product.url) {
                                window.open(product.url, '_blank');
                            }
                        }}
                    >
                        +
                    </button>
                </div>
            </div>

            {showDebug && <div className="debug-overlay">Gallery / {GENRE_NAMES[genre]}</div>}
        </div>
    );
};
