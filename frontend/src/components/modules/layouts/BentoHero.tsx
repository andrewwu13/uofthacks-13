import React from 'react';
import { GENRE_NAMES, BENTO_TYPE_NAMES } from '../../../schema/types';
import type { BentoLayoutProps } from './types';

/**
 * BentoHero - Large featured bento grid item (2x2)
 * Displays a product with a large hero image and prominent content
 */
export const BentoHero: React.FC<BentoLayoutProps> = ({
    product,
    genre,
    bentoType,
    className = '',
    moduleId,
    semanticId
}) => {
    const price = parseFloat(product.price.toString()) || 0;

    return (
        <div
            className={`bento-item bento-hero genre-${GENRE_NAMES[genre].toLowerCase()} ${className}`}
            data-genre={GENRE_NAMES[genre]}
            data-bento-type={BENTO_TYPE_NAMES[bentoType]}
            data-module-id={moduleId}
            data-semantic-id={semanticId}
        >
            {product.imageUrl && (
                <img
                    src={product.imageUrl}
                    alt={product.title}
                    className="product-img hero-img"
                    loading="lazy"
                />
            )}

            <div className="bento-content">
                <h3 className="title">{product.title}</h3>
                <div className="price">${price.toFixed(2)}</div>
            </div>

        </div>
    );
};

export default BentoHero;
