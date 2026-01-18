import { Genre, ShopifyProduct, ProductModule } from '../schema/types';

let moduleCounter = 0;

/**
 * Create product modules from API data with minimal genre (baseline for profile evolution)
 */
export function createProductModules(products: ShopifyProduct[]): ProductModule[] {
    return products.map((product) => {
        moduleCounter++;
        // Start with BASE genre as neutral baseline (previously minimalist)
        const genre = Genre.BASE;

        return {
            id: `product-${moduleCounter}-${product.id}`,
            product,
            genre
        };
    });
}

/**
 * Create a batch of product modules for infinite scroll
 * Samples templateId from the provided random pool.
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
        const randomPoolIndex = Math.floor(Math.random() * idPool.length);
        const templateId = idPool[randomPoolIndex];

        // Fallback genre (derived or default)
        const genre = Genre.BASE;

        moduleCounter++;
        modules.push({
            id: `product-${moduleCounter}-${product.id}-${Date.now()}-${i}`,
            product,
            genre,     // Kept for fallback types
            templateId // The driver of the new style
        });
    }

    return modules;
}
