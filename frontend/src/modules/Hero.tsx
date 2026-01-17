/**
 * Hero Module
 * 
 * Large hero section with headline, subtext, and CTA button.
 * Styled dynamically based on genre.
 */

import React from 'react';
import { Genre, GENRE_CSS_CLASSES, GENRE_NAMES, Variation } from '../schema/types';
import type { HeroContent } from '../schema/data';

interface HeroProps {
    genre: Genre;
    variation: Variation;
    content: HeroContent;
    moduleId: number;
}

export const Hero: React.FC<HeroProps> = ({
    genre,
    variation,
    content,
    moduleId
}) => {
    const genreClass = GENRE_CSS_CLASSES[genre];
    const variationClass = `variation-${variation}`;

    // Genre-specific decorations
    const getDecoration = () => {
        switch (genre) {
            case Genre.CYBER: return '> ';
            case Genre.NEOBRUTALIST: return '★ ';
            default: return '';
        }
    };

    return (
        <div
            className={`module-card module-hero ${genreClass} ${variationClass}`}
            data-module-id={moduleId}
            data-genre={GENRE_NAMES[genre]}
            data-type="Hero"
        >
            <div className="hero-content">
                <h1 className="hero-headline">
                    {getDecoration()}{content.headline}
                </h1>
                <p className="hero-subtext">
                    {content.subtext}
                </p>
                <button className="module-btn hero-cta">
                    {content.ctaText}
                </button>
            </div>

            {/* Background decoration for certain genres */}
            {genre === Genre.GLASSMORPHISM && (
                <div className="hero-orb hero-orb-1"></div>
            )}
            {genre === Genre.GLASSMORPHISM && (
                <div className="hero-orb hero-orb-2"></div>
            )}
        </div>
    );
};

export default Hero;
