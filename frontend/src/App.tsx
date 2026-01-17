/**
 * Gen UI - Self-Evolving AI Storefront
 * 
 * Main application component that demonstrates the rendering engine.
 * Features:
 * - 2x3 grid layout with mixed module types
 * - Demo controls to shuffle/randomize modules
 * - Real-time module replacement simulation
 */

import { useState, useCallback } from 'react';
import {
  RenderingEngine,
  generateRandomLayout,
  generateProductShowcase,
  generateStorefrontLayout,
  replaceModule
} from './components/RenderingEngine';
import {
  decodeModuleId,
  Genre,
  encodeModuleId,
  Variation,
  GENRE_NAMES,
  MODULE_TYPE_NAMES
} from './schema/types';
import type { ModuleTag } from './schema/types';

function App() {
  // Layout state - array of module IDs
  const [layoutIds, setLayoutIds] = useState<number[]>(() => generateStorefrontLayout());

  // Track last clicked module for display
  const [lastClicked, setLastClicked] = useState<{ id: number; tag: ModuleTag } | null>(null);

  // Handle module click - log info and potentially trigger replacement
  const handleModuleClick = useCallback((moduleId: number, tag: ModuleTag) => {
    setLastClicked({ id: moduleId, tag });
    console.log('Module clicked:', {
      id: moduleId,
      genre: GENRE_NAMES[tag.genre],
      type: MODULE_TYPE_NAMES[tag.moduleType],
      variation: tag.variation,
      canReplace: MODULE_TYPE_NAMES[tag.canReplace]
    });
  }, []);

  // Shuffle all modules randomly
  const handleShuffle = () => {
    setLayoutIds(generateRandomLayout(6));
    setLastClicked(null);
  };

  // Show all product cards (different genres)
  const handleProductShowcase = () => {
    setLayoutIds(generateProductShowcase());
    setLastClicked(null);
  };

  // Show mixed storefront layout
  const handleStorefrontLayout = () => {
    setLayoutIds(generateStorefrontLayout());
    setLastClicked(null);
  };

  // Replace a specific module with random genre of same type
  const handleReplaceRandom = (index: number) => {
    setLayoutIds(prev => replaceModule(prev, index));
  };

  // Replace all modules with same type but different genres
  const handleGenreSweep = () => {
    // Get current module types and sweep through all genres
    const currentTags = layoutIds.map(id => decodeModuleId(id));
    const newIds = currentTags.map((tag, i) =>
      encodeModuleId(
        i as Genre, // Each slot gets a different genre
        tag.moduleType,
        tag.variation
      )
    );
    setLayoutIds(newIds);
    setLastClicked(null);
  };

  // Simulate backend pushing new module (random replacement)
  const handleSimulateBackendPush = () => {
    const randomIndex = Math.floor(Math.random() * layoutIds.length);
    const randomGenre = Math.floor(Math.random() * 6) as Genre;
    const randomVariation = Math.floor(Math.random() * 3) as Variation;

    setLayoutIds(prev => replaceModule(prev, randomIndex, randomGenre, randomVariation));
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <h1>GEN UI: Self-Evolving Storefront</h1>
        <p>
          108 module templates (6 genres × 6 types × 3 variations) •
          Click any module to inspect
        </p>
        <p style={{ color: '#737373', fontSize: '0.75rem', marginTop: '0.5rem' }}>
          <a href="/tracking-test.html" style={{ color: '#6366f1' }}>/tracking-test.html</a> to test telemetry tracking
        </p>

        {/* Control Buttons */}
        <div className="app-controls">
          <button onClick={handleShuffle}>🎲 Random Layout</button>
          <button onClick={handleProductShowcase}>🛍️ Product Showcase</button>
          <button onClick={handleStorefrontLayout}>🏪 Storefront Layout</button>
          <button onClick={handleGenreSweep}>🎨 Genre Sweep</button>
          <button onClick={handleSimulateBackendPush}>⚡ Simulate Update</button>
        </div>

        {/* Module Info Display */}
        {lastClicked && (
          <div style={{
            marginTop: '1rem',
            padding: '0.75rem 1rem',
            background: 'rgba(59, 130, 246, 0.1)',
            borderRadius: '8px',
            fontSize: '0.875rem',
            display: 'inline-block'
          }}>
            <strong>Selected:</strong>{' '}
            ID {lastClicked.id} • {GENRE_NAMES[lastClicked.tag.genre]} • {MODULE_TYPE_NAMES[lastClicked.tag.moduleType]}
            {' '}
            <button
              onClick={() => {
                const index = layoutIds.indexOf(lastClicked.id);
                if (index !== -1) handleReplaceRandom(index);
              }}
              style={{
                marginLeft: '0.5rem',
                padding: '0.25rem 0.5rem',
                background: '#3b82f6',
                color: '#fff',
                border: 'none',
                borderRadius: '4px',
                fontSize: '0.75rem',
                cursor: 'pointer'
              }}
            >
              Replace
            </button>
          </div>
        )}
      </header>

      {/* Rendering Engine */}
      <RenderingEngine
        moduleIds={layoutIds}
        onModuleClick={handleModuleClick}
      />

      {/* Debug Info */}
      <footer style={{
        padding: '1rem 2rem',
        borderTop: '1px solid rgba(255, 255, 255, 0.1)',
        fontSize: '0.75rem',
        color: '#71717a',
        textAlign: 'center'
      }}>
        Current Layout IDs: [{layoutIds.join(', ')}]
      </footer>
    </div>
  );
}

export default App;
