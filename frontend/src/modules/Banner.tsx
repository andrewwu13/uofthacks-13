/**
 * Banner Module
 * 
 * Promotional banner with text, highlight, and optional icon.
 * Styled dynamically based on genre.
 */

import React from 'react';
import { Genre, GENRE_CSS_CLASSES, GENRE_NAMES, Variation } from '../schema/types';
import type { BannerContent } from '../schema/data';

interface BannerProps {
    genre: Genre;
    variation: Variation;
    content: BannerContent;
    moduleId: number;
}

export const Banner: React.FC<BannerProps> = ({
    genre,
    variation,
    content,
    moduleId
}) => {
    const genreClass = GENRE_CSS_CLASSES[genre];
    const variationClass = `variation-${variation}`;

    return (
        <div
            className={`module-card module-banner ${genreClass} ${variationClass}`}
            data-module-id={moduleId}
            data-genre={GENRE_NAMES[genre]}
            data-type="Banner"
        >
            <div className="banner-content">
                {content.icon && (
                    <span className="banner-icon">{content.icon}</span>
                )}
                <span className="banner-text">
                    {content.text} <strong className="banner-highlight">{content.highlight}</strong>
                </span>
            </div>
        </div>
    );
};

export default Banner;
