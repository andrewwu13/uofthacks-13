/**
 * ProductCard Module
 * 
 * Displays a product with image, title, description, price, and action button.
 * Styled dynamically based on genre.
 */

import React from 'react';
import { Genre, GENRE_CSS_CLASSES, GENRE_NAMES, Variation } from '../schema/types';
import type { ProductData } from '../schema/types';

interface ProductCardProps {
    genre: Genre;
    variation: Variation;
    product: ProductData;
    moduleId: number;
}

export const ProductCard: React.FC<ProductCardProps> = ({
    genre,
    variation,
    product,
    moduleId
}) => {
    const genreClass = GENRE_CSS_CLASSES[genre];
    const variationClass = `variation-${variation}`;

    // Genre-specific button text
    const getButtonText = () => {
        switch (genre) {
            case Genre.NEOBRUTALIST: return 'BUY NOW';
            case Genre.LOUD: return 'ADD TO CART 🔥';
            case Genre.CYBER: return '>> ACQUIRE';
            case Genre.MINIMALIST: return 'Add';
            default: return 'Add to Cart';
        }
    };

    // Genre-specific badge
    const getBadge = () => {
        if (genre === Genre.LOUD) return { text: 'HOT', show: true };
        if (genre === Genre.NEOBRUTALIST) return { text: 'NEW', show: true };
        if (genre === Genre.CYBER) return { text: 'LIVE', show: true };
        return { text: '', show: false };
    };

    const badge = getBadge();

    return (
        <div
            className={`module-card module-product-card ${genreClass} ${variationClass}`}
            data-module-id={moduleId}
            data-genre={GENRE_NAMES[genre]}
            data-type="ProductCard"
        >
            {/* Badge */}
            {badge.show && (
                <div className="module-badge">{badge.text}</div>
            )}

            {/* Product Image */}
            <div className="product-image-container">
                <img
                    src={product.imageUrl}
                    alt={product.title}
                    className="product-image"
                    loading="lazy"
                />
            </div>

            {/* Product Info */}
            <div className="product-info">
                <span className="product-vendor">{product.vendor}</span>
                <h3 className="product-title">{product.title}</h3>
                <p className="product-description">{product.description}</p>
                <div className="product-price">
                    <span className="price-currency">{product.currency}</span>
                    <span className="price-amount">${product.price.toFixed(2)}</span>
                </div>
            </div>

            {/* Action Button */}
            <button className="module-btn">
                {getButtonText()}
            </button>
        </div>
    );
};

export default ProductCard;
