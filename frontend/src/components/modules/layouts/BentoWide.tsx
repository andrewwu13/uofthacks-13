import React from 'react';
import { GENRE_NAMES, BENTO_TYPE_NAMES } from '../../../schema/types';
import type { BentoLayoutProps } from './types';

/**
 * BentoWide - Horizontal bento grid item (2x1)
 * Displays a product with side-by-side image and content
 */
export const BentoWide: React.FC<BentoLayoutProps> = ({
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
            className={`bento-item bento-wide genre-${GENRE_NAMES[genre].toLowerCase()} ${className}`}
            data-genre={GENRE_NAMES[genre]}
            data-bento-type={BENTO_TYPE_NAMES[bentoType]}
            data-module-id={moduleId}
            data-semantic-id={semanticId}
        >
            <div className="bento-content">
                <h3 className="title">{product.title}</h3>
                <div className="price">${price.toFixed(2)}</div>
            </div>

            {product.imageUrl && (
                <img
                    src={product.imageUrl}
                    alt={product.title}
                    className="product-img wide-img"
                    loading="eager"
                />
            )}

        </div>
    );
};

export default BentoWide;
