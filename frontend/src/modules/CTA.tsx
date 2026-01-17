/**
 * CTA Module
 * 
 * Call-to-action block with headline, subtext, and button.
 * Styled dynamically based on genre.
 */

import React from 'react';
import { Genre, GENRE_CSS_CLASSES, GENRE_NAMES, Variation } from '../schema/types';
import type { CTAContent } from '../schema/data';

interface CTAProps {
    genre: Genre;
    variation: Variation;
    content: CTAContent;
    moduleId: number;
}

export const CTA: React.FC<CTAProps> = ({
    genre,
    variation,
    content,
    moduleId
}) => {
    const genreClass = GENRE_CSS_CLASSES[genre];
    const variationClass = `variation-${variation}`;

    return (
        <div
            className={`module-card module-cta ${genreClass} ${variationClass}`}
            data-module-id={moduleId}
            data-genre={GENRE_NAMES[genre]}
            data-type="CTA"
        >
            <div className="cta-content">
                <h2 className="cta-headline">{content.headline}</h2>
                <p className="cta-subtext">{content.subtext}</p>
                <button className="module-btn cta-button">
                    {content.buttonText}
                </button>
            </div>
        </div>
    );
};

export default CTA;
