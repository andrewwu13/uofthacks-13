/**
 * FeatureList Module
 * 
 * Displays a list of feature highlights with icons.
 * Styled dynamically based on genre.
 */

import React from 'react';
import { Genre, GENRE_CSS_CLASSES, GENRE_NAMES, Variation } from '../schema/types';
import type { FeatureItem } from '../schema/data';

interface FeatureListProps {
    genre: Genre;
    variation: Variation;
    features: FeatureItem[];
    moduleId: number;
}

export const FeatureList: React.FC<FeatureListProps> = ({
    genre,
    variation,
    features,
    moduleId
}) => {
    const genreClass = GENRE_CSS_CLASSES[genre];
    const variationClass = `variation-${variation}`;

    return (
        <div
            className={`module-card module-feature-list ${genreClass} ${variationClass}`}
            data-module-id={moduleId}
            data-genre={GENRE_NAMES[genre]}
            data-type="FeatureList"
        >
            <h3 className="feature-list-title">Why Choose Us</h3>
            <div className="feature-items">
                {features.map((feature, index) => (
                    <div key={index} className="feature-item">
                        <span className="feature-icon">{feature.icon}</span>
                        <div className="feature-content">
                            <h4 className="feature-title">{feature.title}</h4>
                            <p className="feature-description">{feature.description}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default FeatureList;
