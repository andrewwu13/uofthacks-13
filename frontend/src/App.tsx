/**
 * Gen UI - Self-Evolving AI Storefront
 * 
 * Main application component that displays real Shopify products
 * with different visual genre styles.
 * 
 * Features:
 * - Fetches real products from backend (Shopify scraper)
 * - 3-column grid layout with infinite scroll
 * - 6 visual genres for product cards
 * - Dynamic genre assignment
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import {
  RenderingEngine,
  createProductModules,
  createProductBatch
} from './components/RenderingEngine';
import type { ProductModule } from './components/RenderingEngine';
import { fetchProducts } from './api/products';
import type { ShopifyProduct } from './api/products';
import { Genre, GENRE_NAMES } from './schema/types';

function App() {
  // All products loaded from API
  const [allProducts, setAllProducts] = useState<ShopifyProduct[]>([]);

  // Current modules being displayed
  const [modules, setModules] = useState<ProductModule[]>([]);

  // Loading states
  const [isInitialLoading, setIsInitialLoading] = useState(true);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const isLoadingMoreRef = useRef(false);

  // Error state
  const [error, setError] = useState<string | null>(null);

  // Track last clicked product for display
  const [lastClicked, setLastClicked] = useState<{ product: ShopifyProduct; genre: Genre } | null>(null);

  // Fetch products on startup
  useEffect(() => {
    async function loadProducts() {
      setIsInitialLoading(true);
      setError(null);

      try {
        const products = await fetchProducts();

        if (products.length === 0) {
          setError('No products found. Make sure the backend is running and products are scraped.');
          setIsInitialLoading(false);
          return;
        }

        setAllProducts(products);

        // Create initial set of modules (6 products)
        const initialProducts = products.slice(0, 6);
        const initialModules = createProductModules(initialProducts);
        setModules(initialModules);

        console.log(`Loaded ${products.length} products, displaying first 6`);
      } catch (err) {
        setError('Failed to load products. Make sure the backend server is running.');
        console.error('Error loading products:', err);
      } finally {
        setIsInitialLoading(false);
      }
    }

    loadProducts();
  }, []);

  // Handle product click
  const handleModuleClick = useCallback((product: ShopifyProduct, genre: Genre) => {
    setLastClicked({ product, genre });
    console.log('Product clicked:', {
      id: product.id,
      title: product.title,
      genre: GENRE_NAMES[genre],
      store: product.store_domain,
      price: product.price
    });
  }, []);

  // Load more products when scrolling (infinite scroll)
  const handleLoadMore = useCallback(() => {
    if (isLoadingMoreRef.current || allProducts.length === 0) return;
    isLoadingMoreRef.current = true;
    setIsLoadingMore(true);

    // Create new product modules with random genres
    const newModules = createProductBatch(allProducts, modules.length, 3);

    setModules(prev => [...prev, ...newModules]);

    // Small delay before allowing next load
    setTimeout(() => {
      isLoadingMoreRef.current = false;
      setIsLoadingMore(false);
    }, 100);

    console.log('Loaded 3 more products, total:', modules.length + 3);
  }, [allProducts, modules.length]);

  // Shuffle genres for all modules
  const handleGenreShuffle = () => {
    setModules(prev => prev.map(module => ({
      ...module,
      id: `${module.id}-reshuffled-${Date.now()}`,
      genre: Math.floor(Math.random() * 6) as Genre
    })));
    setLastClicked(null);
  };

  // Reset to initial state
  const handleReset = () => {
    if (allProducts.length > 0) {
      const initialProducts = allProducts.slice(0, 6);
      const initialModules = createProductModules(initialProducts);
      setModules(initialModules);
    }
    setLastClicked(null);
  };

  // Group by genre
  const handleGroupByGenre = () => {
    if (allProducts.length < 6) return;

    const genreModules: ProductModule[] = [];
    for (let genre = 0; genre < 6; genre++) {
      const product = allProducts[genre % allProducts.length];
      genreModules.push({
        id: `genre-showcase-${genre}-${Date.now()}`,
        product,
        genre: genre as Genre
      });
    }
    setModules(genreModules);
    setLastClicked(null);
  };

  // Loading state
  if (isInitialLoading) {
    return (
      <div className="app-container">
        <div className="loading-screen">
          <div className="loading-spinner"></div>
          <h2>Loading Products...</h2>
          <p>Fetching from Shopify stores</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="app-container">
        <div className="error-screen">
          <h2>⚠️ Error Loading Products</h2>
          <p>{error}</p>
          <p style={{ marginTop: '1rem', color: '#71717a', fontSize: '0.875rem' }}>
            1. Start the backend: <code>cd backend && uvicorn app.main:app --reload</code><br />
            2. Run the scraper: <code>python -m backend.app.services.shopify_service</code>
          </p>
          <button onClick={() => window.location.reload()} style={{ marginTop: '1rem' }}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <h1>GEN UI: Self-Evolving Storefront</h1>
        <p>
          Real Products from Shopify • 6 Visual Genres • Infinite Scroll
        </p>
        <p style={{ color: '#10b981', fontSize: '0.875rem', marginTop: '0.5rem' }}>
          📦 {allProducts.length} products loaded • Displaying {modules.length} • Scroll for more
        </p>

        {/* Control Buttons */}
        <div className="app-controls">
          <button onClick={handleReset}>🔄 Reset (6)</button>
          <button onClick={handleGenreShuffle}>🎨 Shuffle Genres</button>
          <button onClick={handleGroupByGenre}>📊 Genre Showcase</button>
        </div>

        {/* Product Info Display */}
        {lastClicked && (
          <div style={{
            marginTop: '1rem',
            padding: '0.75rem 1rem',
            background: 'rgba(59, 130, 246, 0.1)',
            borderRadius: '8px',
            fontSize: '0.875rem',
            display: 'inline-block',
            textAlign: 'left'
          }}>
            <strong>Selected:</strong> {lastClicked.product.title}<br />
            <span style={{ color: '#71717a' }}>
              {GENRE_NAMES[lastClicked.genre]} • ${parseFloat(lastClicked.product.price).toFixed(2)} • {lastClicked.product.store_domain}
            </span>
          </div>
        )}
      </header>

      {/* Rendering Engine with Infinite Scroll */}
      <RenderingEngine
        modules={modules}
        onModuleClick={handleModuleClick}
        showDebugInfo={true}
        onLoadMore={handleLoadMore}
        isLoading={isLoadingMore}
      />

      {/* Debug Info */}
      <footer style={{
        padding: '1rem 2rem',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        fontSize: '0.75rem',
        color: '#71717a',
        textAlign: 'center'
      }}>
        Products: {modules.length} displayed / {allProducts.length} total • Scroll down for more
      </footer>
    </div>
  );
}

export default App;
