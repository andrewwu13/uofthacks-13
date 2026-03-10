import React from 'react';
import { GENRE_NAMES, BENTO_TYPE_NAMES } from '../../../schema/types';
import type { BentoLayoutProps } from './types';

/**
 * BentoTall - Vertical bento grid item (1x2)
 * Displays a product with tall image and content below
 */
export const BentoTall: React.FC<BentoLayoutProps> = ({
    product,
    genre,
    bentoType,
    onAddToCart: _onAddToCart,
    className = '',
    moduleId,
    semanticId
}) => {
    const price = parseFloat(product.price.toString()) || 0;

    return (
        <a
            href={product.url}
            target="_blank"
            rel="noopener noreferrer"
            className={`bento-item bento-tall genre-${GENRE_NAMES[genre].toLowerCase()} ${className}`}
            data-genre={GENRE_NAMES[genre]}
            data-bento-type={BENTO_TYPE_NAMES[bentoType]}
            data-module-id={moduleId}
            data-semantic-id={semanticId}
        >
            {product.imageUrl && (
                <img
                    src={product.imageUrl}
                    alt={product.title}
                    className="product-img tall-img"
                    loading="eager"
                    fetchPriority="high"
                />
            )}

            <div className="bento-content">
                <h3 className="title">{product.title}</h3>
                <div className="price">${price.toFixed(2)}</div>
            </div>
        </a>
    );
};

export default BentoTall;
