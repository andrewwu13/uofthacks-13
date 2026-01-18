/**
 * Visual Features for Module Vectorization
 * 
 * Each module template has a numerical feature vector describing its visual properties.
 * These values (0.0 - 1.0) enable ML-based recommendations and similarity calculations.
 * 
 * 11 Dimensions:
 * - genre_id: Genre index normalized (0.0 - 1.0)
 * - curvature: Border radius / roundness
 * - contrast: Text/background contrast level
 * - color_warmth: Cool ↔ Warm color temperature
 * - color_saturation: Muted ↔ Vibrant colors
 * - motion_intensity: Animation/glow effects
 * - visual_density: Sparse ↔ Dense layout
 * - border_weight: Border thickness
 * - font_weight: Light ↔ Bold typography
 * - animation_duration: Short ↔ Long animations
 * - shadow_depth: No shadow ↔ Deep shadow
 */

import { Genre, GENRE_NAMES } from './types';

// ============================================
// VISUAL FEATURE VECTOR TYPE
// ============================================

export interface VisualFeatureVector {
    // Identification
    genre_id: number;         // 0.0 - 1.0 (genre / 5)
    genre_name: string;       // Human-readable genre name

    // Core Visual Properties (0.0 - 1.0)
    curvature: number;        // Border radius: 0 = sharp, 1 = very rounded
    contrast: number;         // Text/BG contrast: 0 = low, 1 = high
    color_warmth: number;     // 0 = cool/cyber, 1 = warm/loud
    color_saturation: number; // 0 = muted, 1 = vibrant
    motion_intensity: number; // 0 = static, 1 = animated/glowing
    visual_density: number;   // 0 = sparse/minimal, 1 = dense
    border_weight: number;    // 0 = none/thin, 1 = thick brutalist

    // Extended Properties
    font_weight: number;      // 0 = light, 1 = heavy/bold
    animation_duration: number; // 0 = instant, 1 = long/slow
    shadow_depth: number;     // 0 = flat/no shadow, 1 = deep shadow
}

// ============================================
// GENRE VISUAL PROFILES
// ============================================

/**
 * Predefined visual profiles for each genre.
 * These values are derived from the CSS definitions in index.css
 */
export const GENRE_VISUAL_PROFILES: Record<Genre, Omit<VisualFeatureVector, 'genre_id' | 'genre_name'>> = {
    // GENRE 0: BASE - Clean, professional dark UI
    [Genre.BASE]: {
        curvature: 0.5,          // 12px radius - moderate
        contrast: 0.6,           // Good contrast on dark
        color_warmth: 0.4,       // Slightly cool (blue accent)
        color_saturation: 0.4,   // Moderate saturation
        motion_intensity: 0.1,   // Minimal animation
        visual_density: 0.5,     // Balanced density
        border_weight: 0.2,      // Thin borders
        font_weight: 0.5,        // Medium weight
        animation_duration: 0.3, // Standard transitions
        shadow_depth: 0.3,       // Subtle shadows
    },

    // GENRE 1: MINIMALIST - Stark, high contrast, Swiss-inspired
    [Genre.MINIMALIST]: {
        curvature: 0.0,          // 0px radius - sharp corners
        contrast: 1.0,           // Maximum contrast (black/white)
        color_warmth: 0.3,       // Cool, neutral
        color_saturation: 0.0,   // No color, monochrome
        motion_intensity: 0.0,   // No animation
        visual_density: 0.2,     // Very sparse
        border_weight: 0.2,      // Thin, precise borders
        font_weight: 0.4,        // Light to medium
        animation_duration: 0.0, // No animations
        shadow_depth: 0.0,       // Flat, no shadow
    },

    // GENRE 2: NEOBRUTALIST - Bold, raw, playful chaos
    [Genre.NEOBRUTALIST]: {
        curvature: 0.0,          // 0px radius - sharp corners
        contrast: 0.9,           // High contrast (yellow/black)
        color_warmth: 0.7,       // Warm yellow
        color_saturation: 1.0,   // Maximum saturation
        motion_intensity: 0.2,   // Subtle hover effects
        visual_density: 0.7,     // Dense, chunky
        border_weight: 1.0,      // Thick 4px borders
        font_weight: 0.9,        // Heavy, bold
        animation_duration: 0.2, // Quick, snappy
        shadow_depth: 0.8,       // Hard offset shadows
    },

    // GENRE 3: GLASSMORPHISM - Ethereal, translucent, dreamy
    [Genre.GLASSMORPHISM]: {
        curvature: 1.0,          // 20px radius - very rounded
        contrast: 0.4,           // Low contrast (translucent)
        color_warmth: 0.5,       // Neutral with purple accent
        color_saturation: 0.5,   // Moderate pastels
        motion_intensity: 0.4,   // Subtle blur effects
        visual_density: 0.4,     // Light, airy
        border_weight: 0.1,      // Very thin, glassy
        font_weight: 0.4,        // Light weight
        animation_duration: 0.6, // Smooth, elegant
        shadow_depth: 0.5,       // Soft glow shadows
    },

    // GENRE 4: LOUD - Attention-grabbing, gradient, energetic
    [Genre.LOUD]: {
        curvature: 0.9,          // 24px radius - very rounded
        contrast: 0.7,           // Good contrast on gradient
        color_warmth: 1.0,       // Maximum warm (orange/red)
        color_saturation: 0.9,   // High saturation
        motion_intensity: 0.5,   // Pulse animations
        visual_density: 0.6,     // Moderately dense
        border_weight: 0.0,      // No borders, gradients
        font_weight: 0.8,        // Bold, impactful
        animation_duration: 0.5, // Medium pulse duration
        shadow_depth: 0.7,       // Dramatic colored shadows
    },

    // GENRE 5: CYBER - Matrix, terminal, hacker aesthetic
    [Genre.CYBER]: {
        curvature: 0.1,          // 4px radius - nearly sharp
        contrast: 0.8,           // High (green on black)
        color_warmth: 0.0,       // Maximum cool (green)
        color_saturation: 0.7,   // Neon green saturation
        motion_intensity: 0.8,   // Glow/flicker animations
        visual_density: 0.5,     // Data-like density
        border_weight: 0.3,      // Dashed terminal borders
        font_weight: 0.5,        // Monospace medium
        animation_duration: 0.9, // Slow glow cycles
        shadow_depth: 0.4,       // Neon glow effect
    },
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Get the complete visual feature vector for a genre
 */
export function getVisualFeatureVector(genre: Genre): VisualFeatureVector {
    const profile = GENRE_VISUAL_PROFILES[genre];

    return {
        genre_id: genre / 5, // Normalize to 0.0 - 1.0
        genre_name: GENRE_NAMES[genre],
        ...profile,
    };
}

/**
 * Get all visual feature vectors as an array (for batch processing)
 */
export function getAllVisualFeatureVectors(): VisualFeatureVector[] {
    return Object.keys(Genre)
        .filter(key => typeof Genre[key as keyof typeof Genre] === 'number')
        .map(key => getVisualFeatureVector(Genre[key as keyof typeof Genre] as Genre));
}

/**
 * Convert a visual feature vector to a numerical array for ML
 * Returns: [genre_id, curvature, contrast, warmth, saturation, motion, density, border, font, animation, shadow]
 */
export function vectorToArray(vector: VisualFeatureVector): number[] {
    return [
        vector.genre_id,
        vector.curvature,
        vector.contrast,
        vector.color_warmth,
        vector.color_saturation,
        vector.motion_intensity,
        vector.visual_density,
        vector.border_weight,
        vector.font_weight,
        vector.animation_duration,
        vector.shadow_depth,
    ];
}

/**
 * Calculate Euclidean distance between two visual feature vectors
 * Lower distance = more similar
 */
export function vectorDistance(a: VisualFeatureVector, b: VisualFeatureVector): number {
    const arrA = vectorToArray(a);
    const arrB = vectorToArray(b);

    let sumSquares = 0;
    for (let i = 0; i < arrA.length; i++) {
        sumSquares += Math.pow(arrA[i] - arrB[i], 2);
    }

    return Math.sqrt(sumSquares);
}

/**
 * Calculate cosine similarity between two visual feature vectors
 * Returns: -1 to 1 (1 = identical direction)
 */
export function cosineSimilarity(a: VisualFeatureVector, b: VisualFeatureVector): number {
    const arrA = vectorToArray(a);
    const arrB = vectorToArray(b);

    let dotProduct = 0;
    let magA = 0;
    let magB = 0;

    for (let i = 0; i < arrA.length; i++) {
        dotProduct += arrA[i] * arrB[i];
        magA += arrA[i] * arrA[i];
        magB += arrB[i] * arrB[i];
    }

    const magnitude = Math.sqrt(magA) * Math.sqrt(magB);
    return magnitude === 0 ? 0 : dotProduct / magnitude;
}

/**
 * Find the most similar genre to a given preference vector
 */
export function findMostSimilarGenre(preferenceVector: number[]): Genre {
    let bestGenre: Genre = Genre.BASE;
    let bestSimilarity = -Infinity;

    for (let genre = 0; genre < 6; genre++) {
        const genreVector = getVisualFeatureVector(genre as Genre);
        const genreArray = vectorToArray(genreVector);

        // Calculate cosine similarity
        let dotProduct = 0;
        let magPref = 0;
        let magGenre = 0;

        for (let i = 0; i < preferenceVector.length && i < genreArray.length; i++) {
            dotProduct += preferenceVector[i] * genreArray[i];
            magPref += preferenceVector[i] * preferenceVector[i];
            magGenre += genreArray[i] * genreArray[i];
        }

        const similarity = dotProduct / (Math.sqrt(magPref) * Math.sqrt(magGenre));

        if (similarity > bestSimilarity) {
            bestSimilarity = similarity;
            bestGenre = genre as Genre;
        }
    }

    return bestGenre;
}

// ============================================
// FEATURE DIMENSION METADATA
// ============================================

export const FEATURE_DIMENSIONS = [
    { key: 'genre_id', label: 'Genre', description: 'Normalized genre index (0-5)' },
    { key: 'curvature', label: 'Curvature', description: 'Border radius / roundness' },
    { key: 'contrast', label: 'Contrast', description: 'Text/background contrast level' },
    { key: 'color_warmth', label: 'Color Warmth', description: 'Cool ↔ Warm temperature' },
    { key: 'color_saturation', label: 'Saturation', description: 'Muted ↔ Vibrant colors' },
    { key: 'motion_intensity', label: 'Motion', description: 'Animation intensity' },
    { key: 'visual_density', label: 'Density', description: 'Sparse ↔ Dense layout' },
    { key: 'border_weight', label: 'Border', description: 'Border thickness' },
    { key: 'font_weight', label: 'Font Weight', description: 'Light ↔ Bold typography' },
    { key: 'animation_duration', label: 'Animation Duration', description: 'Short ↔ Long animations' },
    { key: 'shadow_depth', label: 'Shadow Depth', description: 'Flat ↔ Deep shadow' },
] as const;

export type FeatureDimensionKey = typeof FEATURE_DIMENSIONS[number]['key'];
