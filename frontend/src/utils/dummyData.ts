import { Genre, BentoType, encodeModuleId, decodeModuleId, type ShopifyProduct, type ProductModule } from '../schema/types';

// Drafting site genres (0-5) have visual styling
const DRAFTING_GENRES: Genre[] = [
    Genre.GLASSMORPHISM,
    Genre.BRUTALISM,
    Genre.NEUMORPHISM,
    Genre.CYBERPUNK,
    Genre.MINIMALIST,
    Genre.MONOPRINT
];

// Bento types for variety
const BENTO_TYPES: BentoType[] = [
    BentoType.HERO,
    BentoType.WIDE,
    BentoType.TALL,
    BentoType.SMALL
];

let moduleCounter = 0;

/**
 * Get a drafting site genre (0-5) for visual variety
 */
function getDraftingGenre(index: number): Genre {
    return DRAFTING_GENRES[index % DRAFTING_GENRES.length];
}

/**
 * Get a bento type for variety
 */
function getBentoType(index: number): BentoType {
    return BENTO_TYPES[index % BENTO_TYPES.length];
}

/**
 * Generate template ID for a specific genre and bento type
 */
function generateTemplateId(genre: Genre, bentoType: BentoType, variation: number = 0): number {
    return encodeModuleId(genre, bentoType, variation as 0 | 1 | 2);
}

/**
 * Create product modules from API data with drafting site genre styling
 * (Glassmorphism, Brutalism, Neumorphism, Cyberpunk, Minimalist, Monoprint)
 */
export function createProductModules(products: ShopifyProduct[]): ProductModule[] {
    return products.map((product, index) => {
        moduleCounter++;
        // Use drafting site genres (0-5) for visual styling
        const genre = getDraftingGenre(index);
        const bentoType = getBentoType(index);
        const templateId = generateTemplateId(genre, bentoType);

        return {
            id: `product-${moduleCounter}-${product.id}`,
            product,
            genre,
            bentoType,
            templateId
        };
    });
}

/**
 * Create a batch of product modules for infinite scroll
 * Uses drafting site genres (0-5) for visual variety
 */
export function createProductBatch(
    allProducts: ShopifyProduct[],
    currentCount: number,
    batchSize: number = 3,
    idPool: number[] = [0] // Default pool if not provided
): ProductModule[] {
    const modules: ProductModule[] = [];

    for (let i = 0; i < batchSize; i++) {
        // Cycle through products if we run out
        const productIndex = (currentCount + i) % allProducts.length;
        const product = allProducts[productIndex];

        // Sample a Template ID from the pool
        // 50% Small (3), 20% Tall (2), 15% Hero (0), 15% Wide (1)
        const rand = Math.random();
        let bentoType: BentoType;
        if (rand < 0.5) bentoType = BentoType.SMALL;       // Small
        else if (rand < 0.7) bentoType = BentoType.TALL;  // Tall
        else if (rand < 0.85) bentoType = BentoType.HERO; // Hero
        else bentoType = BentoType.WIDE;                 // Wide

        // Derive genre from templateId using the ModuleRegistry's decoding
        // We still need a templateId, so we'll pick one from the pool and then override bentoType
        const randomPoolIndex = Math.floor(Math.random() * idPool.length);
        const templateIdFromPool = idPool[randomPoolIndex];
        const moduleTag = decodeModuleId(templateIdFromPool);
        const genre = moduleTag.genre;

        // Re-encode templateId with the newly sampled bentoType
        const templateId = encodeModuleId(genre, bentoType, moduleTag.variation);

        moduleCounter++;
        modules.push({
            id: `product-${moduleCounter}-${product.id}-${Date.now()}-${i}`,
            product,
            genre,
            bentoType,
            templateId
        });
    }

    return modules;
}
