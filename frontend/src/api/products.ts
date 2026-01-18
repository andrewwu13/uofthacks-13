/**
 * Products API Service
 * 
 * Fetches product data from the backend API.
 * The backend scrapes products from Shopify stores.
 * 
 * Set VITE_USE_MOCK_DATA=true to use mock data without backend.
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
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === 'true';

// Mock products for development without backend
const MOCK_PRODUCTS: ShopifyProduct[] = [
    { id: 1, store_domain: 'mock-store.myshopify.com', title: 'Vintage Leather Backpack', handle: 'vintage-leather-backpack', url: '#', price: '149.99', currency: 'USD', image: 'https://picsum.photos/seed/backpack/400/400', vendor: 'Heritage Goods', description: 'Handcrafted leather backpack with brass fittings' },
    { id: 2, store_domain: 'mock-store.myshopify.com', title: 'Wireless Earbuds Pro', handle: 'wireless-earbuds-pro', url: '#', price: '89.00', currency: 'USD', image: 'https://picsum.photos/seed/earbuds/400/400', vendor: 'AudioTech', description: 'Premium sound with active noise cancellation' },
    { id: 3, store_domain: 'mock-store.myshopify.com', title: 'Minimalist Watch', handle: 'minimalist-watch', url: '#', price: '275.00', currency: 'USD', image: 'https://picsum.photos/seed/watch/400/400', vendor: 'Timekeeper Co', description: 'Swiss movement, sapphire crystal' },
    { id: 4, store_domain: 'mock-store.myshopify.com', title: 'Organic Cotton Hoodie', handle: 'organic-cotton-hoodie', url: '#', price: '68.00', currency: 'USD', image: 'https://picsum.photos/seed/hoodie/400/400', vendor: 'EcoWear', description: 'Sustainably sourced, ultra-soft fabric' },
    { id: 5, store_domain: 'mock-store.myshopify.com', title: 'Smart Home Hub', handle: 'smart-home-hub', url: '#', price: '199.99', currency: 'USD', image: 'https://picsum.photos/seed/smarthome/400/400', vendor: 'HomeTech', description: 'Control all your smart devices from one place' },
    { id: 6, store_domain: 'mock-store.myshopify.com', title: 'Artisan Coffee Beans', handle: 'artisan-coffee-beans', url: '#', price: '24.99', currency: 'USD', image: 'https://picsum.photos/seed/coffee/400/400', vendor: 'Bean Brothers', description: 'Single origin, freshly roasted' },
    { id: 7, store_domain: 'mock-store.myshopify.com', title: 'Running Shoes Elite', handle: 'running-shoes-elite', url: '#', price: '159.00', currency: 'USD', image: 'https://picsum.photos/seed/shoes/400/400', vendor: 'SpeedRun', description: 'Carbon fiber plate for maximum energy return' },
    { id: 8, store_domain: 'mock-store.myshopify.com', title: 'Ceramic Plant Pot Set', handle: 'ceramic-plant-pot-set', url: '#', price: '49.99', currency: 'USD', image: 'https://picsum.photos/seed/pots/400/400', vendor: 'Green Living', description: 'Set of 3 hand-glazed pots with drainage' },
    { id: 9, store_domain: 'mock-store.myshopify.com', title: 'Mechanical Keyboard', handle: 'mechanical-keyboard', url: '#', price: '129.00', currency: 'USD', image: 'https://picsum.photos/seed/keyboard/400/400', vendor: 'TypeMaster', description: 'Cherry MX switches, RGB backlighting' },
    { id: 10, store_domain: 'mock-store.myshopify.com', title: 'Yoga Mat Premium', handle: 'yoga-mat-premium', url: '#', price: '78.00', currency: 'USD', image: 'https://picsum.photos/seed/yoga/400/400', vendor: 'ZenFit', description: 'Extra thick, non-slip surface' },
    { id: 11, store_domain: 'mock-store.myshopify.com', title: 'Desk Lamp LED', handle: 'desk-lamp-led', url: '#', price: '59.99', currency: 'USD', image: 'https://picsum.photos/seed/lamp/400/400', vendor: 'LightWorks', description: 'Adjustable color temperature and brightness' },
    { id: 12, store_domain: 'mock-store.myshopify.com', title: 'Canvas Tote Bag', handle: 'canvas-tote-bag', url: '#', price: '35.00', currency: 'USD', image: 'https://picsum.photos/seed/tote/400/400', vendor: 'CarryAll', description: 'Heavy-duty cotton canvas with leather handles' },
];

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
 * Fetch all products from the backend API (or return mock data in dev mode)
 */
export async function fetchProducts(): Promise<ShopifyProduct[]> {
    // Return mock data if VITE_USE_MOCK_DATA is enabled
    if (USE_MOCK_DATA) {
        console.log('[Mock Mode] Using mock product data (VITE_USE_MOCK_DATA=true)');
        return MOCK_PRODUCTS;
    }

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
