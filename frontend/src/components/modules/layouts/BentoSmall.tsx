import React from 'react';
import { GENRE_NAMES, BENTO_TYPE_NAMES } from '../../../schema/types';
import type { BentoLayoutProps } from './types';

/**
 * BentoSmall - Compact bento grid item (1x1)
 * Displays a product with small thumbnail and minimal content
 */
export const BentoSmall: React.FC<BentoLayoutProps> = ({
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
        <div
            className={`bento-item bento-small genre-${GENRE_NAMES[genre].toLowerCase()} ${className}`}
            data-genre={GENRE_NAMES[genre]}
            data-bento-type={BENTO_TYPE_NAMES[bentoType]}
            data-module-id={moduleId}
            data-semantic-id={semanticId}
        >
            {product.imageUrl && (
                <img
                    src={product.imageUrl}
                    alt={product.title}
                    className="product-img thumb-img"
                    loading="lazy"
                />
            )}

            <div className="bento-content">
                <h4 className="name">{product.title}</h4>
                <div className="price">${price.toFixed(2)}</div>
            </div>

        </div>
    );
};

export default BentoSmall;
