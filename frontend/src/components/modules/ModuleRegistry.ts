import React from 'react';
import {
    Genre,
    BentoType,
    encodeModuleId,
    GENRE_NAMES,
    BENTO_TYPE_NAMES,
    getModuleCssClass,
    generateSemanticId
} from '../../schema/types';

// Bento Layout Components
import { BentoHero } from './layouts/BentoHero';
import { BentoWide } from './layouts/BentoWide';
import { BentoTall } from './layouts/BentoTall';
import { BentoSmall } from './layouts/BentoSmall';
import type { BentoLayoutProps } from './layouts/types';

// Component Map for Bento Types
const BENTO_COMPONENTS: Record<BentoType, React.FC<BentoLayoutProps>> = {
    [BentoType.HERO]: BentoHero,
    [BentoType.WIDE]: BentoWide,
    [BentoType.TALL]: BentoTall,
    [BentoType.SMALL]: BentoSmall
};

export interface ModuleConfig {
    id: number;
    label: string;
    genre: Genre;
    bentoType: BentoType;
    component: React.FC<BentoLayoutProps>;
    className: string;
    semanticId: string;
}

// Generate the registry programmatically for bento modules
const registry: Record<number, ModuleConfig> = {};

// Populate with bento modules: 6 genres × 4 bento types = 24 base modules
// With 3 variations each = 72 total modules
for (let genre = 0; genre < 6; genre++) {
    for (let bentoType = 0; bentoType < 4; bentoType++) {
        // Create entries for each variation (0, 1, 2)
        for (let variation = 0; variation < 3; variation++) {
            const id = encodeModuleId(
                genre as Genre,
                bentoType as BentoType,
                variation as 0 | 1 | 2
            );
            const genreName = GENRE_NAMES[genre as Genre];
            const bentoName = BENTO_TYPE_NAMES[bentoType as BentoType];

            registry[id] = {
                id,
                label: `${genreName} ${bentoName}`,
                genre: genre as Genre,
                bentoType: bentoType as BentoType,
                component: BENTO_COMPONENTS[bentoType as BentoType],
                className: getModuleCssClass(id),
                semanticId: generateSemanticId(genre as Genre, bentoType as BentoType, id)
            };
        }
    }
}

export const MODULE_REGISTRY = registry;

export function getModuleConfig(id: number): ModuleConfig {
    return MODULE_REGISTRY[id] || MODULE_REGISTRY[0]; // Fallback to 0
}

/**
 * Get module config by genre and bento type (defaults to variation 0)
 */
export function getModuleByType(genre: Genre, bentoType: BentoType, variation: number = 0): ModuleConfig {
    const id = encodeModuleId(genre, bentoType, variation as 0 | 1 | 2);
    return getModuleConfig(id);
}
