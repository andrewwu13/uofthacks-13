/**
 * Gen UI - AI-Powered Self-Evolving Storefront
 * Main Application Entry Point
 */

function App() {
  return (
    <div style={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center',
      flexDirection: 'column',
      gap: '1rem',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h1>🚀 Gen UI Storefront</h1>
      <p style={{ color: '#a3a3a3' }}>
        AI-powered self-evolving storefront
      </p>
      <p style={{ color: '#737373', fontSize: '0.875rem' }}>
        Visit <a href="/tracking-test.html" style={{ color: '#6366f1' }}>/tracking-test.html</a> to test the telemetry tracking system
      </p>
    </div>
  );
}

export default App;
