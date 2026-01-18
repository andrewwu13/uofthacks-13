import React from 'react';
import type { Genre as GenreType, LayoutType as LayoutTypeValue } from '../../schema/types';
import {
    Genre,
    LayoutType,
    encodeModuleId,
    GENRE_NAMES,
    LAYOUT_TYPE_NAMES,
    getModuleCssClass
} from '../../schema/types';

// Layout Components
import { StandardCard } from './layouts/StandardCard';
import { CompactList } from './layouts/CompactList';
import { FeaturedHero } from './layouts/FeaturedHero';
import { GalleryView } from './layouts/GalleryView';
import { TechSpec } from './layouts/TechSpec';
import { BoldTypo } from './layouts/BoldTypo';
import type { LayoutProps } from './layouts/types';

// Component Map
const LAYOUT_COMPONENTS: Record<LayoutType, React.FC<LayoutProps>> = {
    [LayoutType.STANDARD]: StandardCard,
    [LayoutType.COMPACT]: CompactList,
    [LayoutType.FEATURED]: FeaturedHero,
    [LayoutType.GALLERY]: GalleryView,
    [LayoutType.TECHNICAL]: TechSpec,
    [LayoutType.BOLD]: BoldTypo
};

export interface ModuleConfig {
    id: number;
    label: string;
    genre: Genre;
    layout: LayoutType;
    component: React.FC<LayoutProps>;
    className: string;
}

// Generate the registry programmatically
const registry: Record<number, ModuleConfig> = {};

// Semantic tags for each generic combo (simplified for client)
const TAGS: Record<Genre, string[]> = {
    [Genre.BASE]: ["classic", "clean"],
    [Genre.MINIMALIST]: ["luxury", "stark"],
    [Genre.NEOBRUTALIST]: ["bold", "raw"],
    [Genre.GLASSMORPHISM]: ["ethereal", "modern"],
    [Genre.LOUD]: ["vibrant", "energetic"],
    [Genre.CYBER]: ["tech", "dark"]
};

// Populate
for (let genre = 0; genre < 6; genre++) {
    for (let layout = 0; layout < 6; layout++) {
        const id = encodeModuleId(genre as Genre, layout as LayoutType);
        const genreName = GENRE_NAMES[genre as Genre];
        const layoutName = LAYOUT_TYPE_NAMES[layout as LayoutType];

        registry[id] = {
            id,
            label: `${genreName} ${layoutName}`,
            genre: genre as Genre,
            layout: layout as LayoutType,
            component: LAYOUT_COMPONENTS[layout as LayoutType],
            className: getModuleCssClass(id),
        };
    }
}

export const MODULE_REGISTRY = registry;

export function getModuleConfig(id: number): ModuleConfig {
    return MODULE_REGISTRY[id] || MODULE_REGISTRY[0]; // Fallback to 0
}
