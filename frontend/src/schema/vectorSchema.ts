/**
 * Vector Schema for Module Matching
 * 
 * 12-dimensional feature space used to represent both UI modules and
 * user profiles for similarity matching. This mirrors the Python
 * implementation in backend/app/vector/.
 * 
 * Dimensions:
 * 0. DARKNESS        - 0=light, 1=dark
 * 1. VIBRANCY        - 0=muted, 1=vibrant
 * 2. CORNER_ROUNDNESS - 0=sharp, 1=pill
 * 3. DENSITY         - 0=low, 1=high
 * 4. TYPOGRAPHY_WEIGHT - 0=light, 1=bold
 * 5. BUTTON_SIZE     - 0=small, 1=large
 * 6. MINIMALISM      - Genre weight
 * 7. BRUTALISM       - Genre weight
 * 8. GLASS_EFFECT    - Genre weight
 * 9. LOUDNESS        - Genre weight (experimental)
 * 10. INTERACTIVITY  - Animation level
 * 11. EXPLORATION    - Novel vs stable preference
 */

// ============================================
// CONSTANTS
// ============================================

export const FEATURE_DIMENSIONS = 12;

// ============================================
// TYPES
// ============================================

export type FeatureVector = number[];

// ============================================
// FEATURE INDEX ENUM
// ============================================

export const FeatureIndex = {
    DARKNESS: 0,
    VIBRANCY: 1,
    CORNER_ROUNDNESS: 2,
    DENSITY: 3,
    TYPOGRAPHY_WEIGHT: 4,
    BUTTON_SIZE: 5,
    MINIMALISM: 6,
    BRUTALISM: 7,
    GLASS_EFFECT: 8,
    LOUDNESS: 9,
    INTERACTIVITY: 10,
    EXPLORATION: 11,
} as const;

export type FeatureIndexKey = keyof typeof FeatureIndex;

// ============================================
// ENCODINGS FOR CATEGORICAL VALUES
// ============================================

export const ENCODINGS: Record<string, Record<string, number>> = {
    // Color scheme: darkness level
    color_scheme: {
        light: 0.0,
        dark: 1.0,
        vibrant: 0.5,
    },
    // Corner radius: roundness level
    corner_radius: {
        sharp: 0.0,
        rounded: 0.5,
        pill: 1.0,
    },
    // Density level
    density: {
        low: 0.0,
        medium: 0.5,
        high: 1.0,
    },
    // Typography weight
    typography_weight: {
        light: 0.0,
        regular: 0.5,
        bold: 1.0,
    },
    // Button size
    button_size: {
        small: 0.0,
        medium: 0.5,
        large: 1.0,
    },
    // Decision confidence → exploration
    decision_confidence: {
        high: 0.2,    // Confident = less exploration
        medium: 0.5,
        low: 0.8,     // Uncertain = more exploration
    },
    // Exploration tolerance
    exploration_tolerance: {
        low: 0.2,
        medium: 0.5,
        high: 0.8,
    },
    // Engagement depth → interactivity preference
    engagement_depth: {
        shallow: 0.2,
        moderate: 0.5,
        deep: 0.8,
    },
};

// ============================================
// GENRE VECTORS
// ============================================

/** 
 * Genre to vector component mapping
 * [minimalism, brutalism, glass, loudness]
 */
export const GENRE_VECTORS: Record<string, [number, number, number, number]> = {
    base: [0.0, 0.0, 0.0, 0.2],
    minimalist: [1.0, 0.0, 0.0, 0.0],
    neobrutalist: [0.0, 1.0, 0.0, 0.3],
    glassmorphism: [0.3, 0.0, 1.0, 0.0],
    loud: [0.0, 0.2, 0.0, 1.0],
    cyber: [0.2, 0.3, 0.2, 0.5],
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Encode a categorical value to a float in [0, 1]
 */
export function encodeValue(category: string, value: string): number {
    if (category in ENCODINGS && value in ENCODINGS[category]) {
        return ENCODINGS[category][value];
    }
    return 0.5; // Default to neutral
}

/**
 * Create a zero/neutral feature vector
 */
export function createZeroVector(): FeatureVector {
    return Array(FEATURE_DIMENSIONS).fill(0.5);
}

/**
 * Normalize vector to unit length for cosine similarity
 */
export function normalizeVector(vector: FeatureVector): FeatureVector {
    const sumSquares = vector.reduce((sum, val) => sum + val * val, 0);
    const norm = Math.sqrt(sumSquares);
    
    if (norm > 0) {
        return vector.map(v => v / norm);
    }
    return [...vector];
}

/**
 * Calculate Euclidean distance between two feature vectors
 * Lower = more similar
 */
export function vectorDistance(a: FeatureVector, b: FeatureVector): number {
    if (a.length !== b.length) {
        throw new Error('Vectors must have the same length');
    }
    
    let sumSquares = 0;
    for (let i = 0; i < a.length; i++) {
        sumSquares += Math.pow(a[i] - b[i], 2);
    }
    
    return Math.sqrt(sumSquares);
}

/**
 * Calculate cosine similarity between two feature vectors
 * Returns: -1 to 1 (1 = identical direction)
 */
export function cosineSimilarity(a: FeatureVector, b: FeatureVector): number {
    if (a.length !== b.length) {
        throw new Error('Vectors must have the same length');
    }
    
    let dotProduct = 0;
    let magA = 0;
    let magB = 0;
    
    for (let i = 0; i < a.length; i++) {
        dotProduct += a[i] * b[i];
        magA += a[i] * a[i];
        magB += b[i] * b[i];
    }
    
    const magProduct = Math.sqrt(magA) * Math.sqrt(magB);
    
    if (magProduct === 0) {
        return 0;
    }
    
    return dotProduct / magProduct;
}

// ============================================
// SEARCH RESULT TYPE
// ============================================

export interface SearchResult {
    id: string;
    score: number;
    vector: FeatureVector;
}

/**
 * Find top-k most similar vectors using cosine similarity
 */
export function findSimilar(
    query: FeatureVector,
    candidates: Array<{ id: string; vector: FeatureVector }>,
    topK: number = 5
): SearchResult[] {
    // Normalize query
    const normalizedQuery = normalizeVector(query);
    
    // Calculate similarities
    const results: SearchResult[] = candidates.map(candidate => {
        const normalizedCandidate = normalizeVector(candidate.vector);
        return {
            id: candidate.id,
            score: cosineSimilarity(normalizedQuery, normalizedCandidate),
            vector: candidate.vector,
        };
    });
    
    // Sort by similarity (descending) and return top-k
    results.sort((a, b) => b.score - a.score);
    return results.slice(0, topK);
}

// ============================================
// PROFILE TYPES (matching Python ReducerOutput)
// ============================================

export interface VisualTraits {
    color_scheme: 'dark' | 'light' | 'vibrant';
    corner_radius: 'sharp' | 'rounded' | 'pill';
    button_size: 'small' | 'medium' | 'large';
    density: 'low' | 'medium' | 'high';
    typography_weight: 'light' | 'regular' | 'bold';
}

export interface InteractionTraits {
    decision_confidence: 'low' | 'medium' | 'high';
    exploration_tolerance: 'low' | 'medium' | 'high';
    scroll_behavior: 'slow' | 'moderate' | 'fast';
}

export interface BehavioralTraits {
    speed_vs_accuracy: 'speed' | 'balanced' | 'accuracy';
    engagement_depth: 'shallow' | 'moderate' | 'deep';
}

export interface UserProfile {
    visual: VisualTraits;
    interaction: InteractionTraits;
    behavioral: BehavioralTraits;
}

/**
 * Default user profile (neutral settings)
 */
export const DEFAULT_PROFILE: UserProfile = {
    visual: {
        color_scheme: 'light',
        corner_radius: 'rounded',
        button_size: 'medium',
        density: 'medium',
        typography_weight: 'regular',
    },
    interaction: {
        decision_confidence: 'medium',
        exploration_tolerance: 'medium',
        scroll_behavior: 'moderate',
    },
    behavioral: {
        speed_vs_accuracy: 'balanced',
        engagement_depth: 'moderate',
    },
};

/**
 * Convert a user profile to a normalized feature vector
 */
export function profileToVector(profile: UserProfile): FeatureVector {
    const vector = Array(FEATURE_DIMENSIONS).fill(0.0);
    
    const { visual, interaction, behavioral } = profile;
    
    // ========================================
    // Visual Traits → Feature Vector
    // ========================================
    
    // Color scheme → darkness & vibrancy
    if (visual.color_scheme === 'dark') {
        vector[FeatureIndex.DARKNESS] = 1.0;
        vector[FeatureIndex.VIBRANCY] = 0.4;
    } else if (visual.color_scheme === 'vibrant') {
        vector[FeatureIndex.DARKNESS] = 0.3;
        vector[FeatureIndex.VIBRANCY] = 1.0;
    } else { // light
        vector[FeatureIndex.DARKNESS] = 0.0;
        vector[FeatureIndex.VIBRANCY] = 0.3;
    }
    
    // Corner radius
    vector[FeatureIndex.CORNER_ROUNDNESS] = encodeValue('corner_radius', visual.corner_radius);
    
    // Density
    vector[FeatureIndex.DENSITY] = encodeValue('density', visual.density);
    
    // Typography weight
    vector[FeatureIndex.TYPOGRAPHY_WEIGHT] = encodeValue('typography_weight', visual.typography_weight);
    
    // Button size
    vector[FeatureIndex.BUTTON_SIZE] = encodeValue('button_size', visual.button_size);
    
    // ========================================
    // Genre Inference from Visual/Behavioral
    // ========================================
    
    // Low density + light weight → minimalist
    const minimalismScore = 
        (1.0 - vector[FeatureIndex.DENSITY]) * 0.5 +
        (1.0 - vector[FeatureIndex.TYPOGRAPHY_WEIGHT]) * 0.3 +
        (1.0 - vector[FeatureIndex.CORNER_ROUNDNESS]) * 0.2;
    
    // High contrast + bold + sharp → brutalist
    const brutalismScore = 
        vector[FeatureIndex.VIBRANCY] * 0.4 +
        vector[FeatureIndex.TYPOGRAPHY_WEIGHT] * 0.4 +
        (1.0 - vector[FeatureIndex.CORNER_ROUNDNESS]) * 0.2;
    
    // Rounded + medium density + blur-friendly → glass
    // Note: Clamping the density term to prevent negative values
    const glassScore = 
        vector[FeatureIndex.CORNER_ROUNDNESS] * 0.5 +
        Math.max(0.0, 1.0 - Math.abs(vector[FeatureIndex.DENSITY] - 0.5) * 2) * 0.3 +
        vector[FeatureIndex.DARKNESS] * 0.2;
    
    // High vibrancy + large buttons + exploration → loud
    const explorationFactor = encodeValue('exploration_tolerance', interaction.exploration_tolerance);
    const loudnessScore = 
        vector[FeatureIndex.VIBRANCY] * 0.4 +
        vector[FeatureIndex.BUTTON_SIZE] * 0.3 +
        explorationFactor * 0.3;
    
    // Clamp all scores to [0.0, 1.0]
    vector[FeatureIndex.MINIMALISM] = Math.max(0.0, Math.min(1.0, minimalismScore));
    vector[FeatureIndex.BRUTALISM] = Math.max(0.0, Math.min(1.0, brutalismScore));
    vector[FeatureIndex.GLASS_EFFECT] = Math.max(0.0, Math.min(1.0, glassScore));
    vector[FeatureIndex.LOUDNESS] = Math.max(0.0, Math.min(1.0, loudnessScore));
    
    // ========================================
    // Behavioral Traits → Interactivity & Exploration
    // ========================================
    
    // Engagement depth → interactivity preference
    vector[FeatureIndex.INTERACTIVITY] = encodeValue('engagement_depth', behavioral.engagement_depth);
    
    // Exploration tolerance
    vector[FeatureIndex.EXPLORATION] = explorationFactor;
    
    return normalizeVector(vector);
}
