/**
 * Products API Service
 * 
 * Fetches product data from the backend API.
 * The backend scrapes products from Shopify stores.
 */

// Product type matching the backend schema
export interface ShopifyProduct {
    id: number;
    store_domain: string;
    title: string;
    handle: string;
    url: string;
    price: string;
    currency: string;
    image: string | null;
    vendor: string;
    description: string | null;
}

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Generate a simple session ID for this browser session
function getSessionId(): string {
    let sessionId = sessionStorage.getItem('genui_session_id');
    if (!sessionId) {
        sessionId = `session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
        sessionStorage.setItem('genui_session_id', sessionId);
    }
    return sessionId;
}

/**
 * Fetch all products from the backend API
 */
export async function fetchProducts(): Promise<ShopifyProduct[]> {
    const sessionId = getSessionId();

    try {
        const response = await fetch(`${API_BASE_URL}/products/${sessionId}`);

        if (!response.ok) {
            console.error('Failed to fetch products:', response.status, response.statusText);
            return [];
        }

        const products: ShopifyProduct[] = await response.json();
        console.log(`Loaded ${products.length} products from API`);
        return products;
    } catch (error) {
        console.error('Error fetching products:', error);
        return [];
    }
}

/**
 * Fetch a batch of products for infinite scroll
 */
export async function fetchProductsBatch(
    allProducts: ShopifyProduct[],
    currentCount: number,
    batchSize: number = 6
): Promise<ShopifyProduct[]> {
    // Get the next batch of products from the loaded array
    const startIndex = currentCount % allProducts.length;
    const batch: ShopifyProduct[] = [];

    for (let i = 0; i < batchSize; i++) {
        const index = (startIndex + i) % allProducts.length;
        batch.push(allProducts[index]);
    }

    return batch;
}

export { getSessionId };
