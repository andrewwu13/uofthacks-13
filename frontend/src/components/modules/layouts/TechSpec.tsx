import React from 'react';
import { GENRE_NAMES } from '../../../schema/types';
import type { LayoutProps } from './types';

export const TechSpec: React.FC<LayoutProps> = ({
    product,
    genre,
    onAddToCart,
    className = '',
    showDebug
}) => {
    return (
        <div
            className={`module-card module-layout-technical ${className}`}
            data-genre={GENRE_NAMES[genre]}
        >
            <div className="tech-header">
                <div className="tech-id">REF: {String(product.id).substring(0, 8)}</div>
                <div className="tech-status">IN_STOCK</div>
            </div>

            <div className="tech-grid">
                <div className="tech-thumb">
                    <img src={product.imageUrl} alt="" className="tech-image" />
                </div>

                <div className="tech-data">
                    <div className="tech-row">
                        <span className="tech-label">MODEL</span>
                        <span className="tech-value">{product.title}</span>
                    </div>
                    <div className="tech-row">
                        <span className="tech-label">MFG</span>
                        <span className="tech-value">{product.vendor}</span>
                    </div>
                    <div className="tech-row">
                        <span className="tech-label">COST</span>
                        <span className="tech-value">${product.price}</span>
                    </div>
                </div>
            </div>

            <button
                className="module-btn tech-btn"
                onClick={(e) => {
                    e.stopPropagation();
                    onAddToCart?.();
                    if (product.url) {
                        window.open(product.url, '_blank');
                    }
                }}
            >
                [INITIATE_ORDER]
            </button>

            {showDebug && <div className="debug-overlay">Tech / {GENRE_NAMES[genre]}</div>}
        </div>
    );
};
