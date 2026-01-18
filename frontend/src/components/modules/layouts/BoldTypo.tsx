import React from 'react';
import { GENRE_NAMES } from '../../../schema/types';
import type { LayoutProps } from './types';

export const BoldTypo: React.FC<LayoutProps> = ({
    product,
    genre,
    onAddToCart,
    className = '',
    showDebug
}) => {
    return (
        <div
            className={`module-card module-layout-bold ${className}`}
            data-genre={GENRE_NAMES[genre]}
        >
            <div className="bold-content">
                <h1 className="bold-title">{product.title}</h1>
                <div className="bold-meta">
                    <span className="bold-vendor">{product.vendor}</span>
                    <span className="bold-price">${product.price}</span>
                </div>
            </div>

            <div className="bold-image-strip">
                <img src={product.imageUrl ?? undefined} alt="" className="bold-image" />
            </div>

            <button
                className="module-btn bold-btn"
                onClick={(e) => {
                    e.stopPropagation();
                    onAddToCart?.();
                    if (product.url) {
                        window.open(product.url, '_blank');
                    }
                }}
            >
                GET IT
            </button>

            {showDebug && <div className="debug-overlay">Bold / {GENRE_NAMES[genre]}</div>}
        </div>
    );
};
