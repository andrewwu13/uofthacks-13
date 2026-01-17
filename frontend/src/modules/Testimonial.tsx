/**
 * Testimonial Module
 * 
 * Customer testimonial with quote, avatar, and author info.
 * Styled dynamically based on genre.
 */

import React from 'react';
import { Genre, GENRE_CSS_CLASSES, GENRE_NAMES, Variation } from '../schema/types';
import type { TestimonialContent } from '../schema/data';

interface TestimonialProps {
    genre: Genre;
    variation: Variation;
    content: TestimonialContent;
    moduleId: number;
}

export const Testimonial: React.FC<TestimonialProps> = ({
    genre,
    variation,
    content,
    moduleId
}) => {
    const genreClass = GENRE_CSS_CLASSES[genre];
    const variationClass = `variation-${variation}`;

    // Quote marks based on genre
    const getQuoteMark = () => {
        switch (genre) {
            case Genre.NEOBRUTALIST: return '★★★★★';
            case Genre.CYBER: return '>> ';
            default: return '"';
        }
    };

    return (
        <div
            className={`module-card module-testimonial ${genreClass} ${variationClass}`}
            data-module-id={moduleId}
            data-genre={GENRE_NAMES[genre]}
            data-type="Testimonial"
        >
            <div className="testimonial-content">
                <div className="testimonial-quote-mark">{getQuoteMark()}</div>
                <blockquote className="testimonial-quote">
                    {content.quote}
                </blockquote>
                <div className="testimonial-author">
                    <img
                        src={`https://picsum.photos/seed/${content.avatarSeed}/80/80`}
                        alt={content.author}
                        className="testimonial-avatar"
                    />
                    <div className="testimonial-author-info">
                        <span className="testimonial-name">{content.author}</span>
                        <span className="testimonial-role">{content.role}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Testimonial;
