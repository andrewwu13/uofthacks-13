/**
 * Tracking Demo Page
 * Mock site to test the telemetry tracking system
 */

import { useEffect, useState, useRef } from 'react';
import { initTelemetry, TelemetryManager } from '../tracking';
import './TrackingDemo.css';

interface MotorState {
  velocity: { x: number; y: number };
  acceleration: { x: number; y: number };
  speed: number;
  jerk: number;
}

function classifyMotorState(state: MotorState): { label: string; color: string } {
  const { speed, jerk } = state;
  
  // Classification based on velocity/acceleration thresholds
  if (speed < 50 && jerk < 1000) {
    return { label: 'Focused', color: '#22c55e' };
  } else if (speed > 500 || jerk > 5000) {
    return { label: 'Anxious', color: '#ef4444' };
  } else if (jerk > 2000 && speed < 200) {
    return { label: 'Indecisive', color: '#f59e0b' };
  } else if (speed > 300 && jerk < 1000) {
    return { label: 'Determined', color: '#3b82f6' };
  }
  return { label: 'Browsing', color: '#a3a3a3' };
}

export function TrackingDemo() {
  const [telemetry, setTelemetry] = useState<TelemetryManager | null>(null);
  const [motorState, setMotorState] = useState<MotorState>({
    velocity: { x: 0, y: 0 },
    acceleration: { x: 0, y: 0 },
    speed: 0,
    jerk: 0,
  });
  const [batchCount, setBatchCount] = useState(0);
  const rafRef = useRef<number | undefined>(undefined);

  useEffect(() => {
    // Initialize telemetry on mount
    const manager = initTelemetry({
      flushInterval: 5000,
      enableConsoleLog: true,
      onBatch: () => {
        setBatchCount(c => c + 1);
      },
    });
    
    setTelemetry(manager);

    // Update motor state in real-time
    const updateMotorState = () => {
      setMotorState(manager.getMotorState());
      rafRef.current = requestAnimationFrame(updateMotorState);
    };
    rafRef.current = requestAnimationFrame(updateMotorState);

    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
      }
      manager.stop();
    };
  }, []);

  const stateClass = classifyMotorState(motorState);

  return (
    <div className="tracking-demo">
      {/* Header with Status */}
      <header className="demo-header">
        <h1>🔍 Telemetry Tracking Demo</h1>
        <div className="demo-status">
          <span className="status-badge" style={{ backgroundColor: stateClass.color }}>
            {stateClass.label}
          </span>
          <span className="batch-counter">Batches: {batchCount}</span>
          {telemetry && (
            <span className="session-id">Session: {telemetry.getSessionId()}</span>
          )}
        </div>
      </header>

      {/* Real-time Motor State Display */}
      <section className="motor-state-panel">
        <h2>Motor State (Real-time)</h2>
        <div className="motor-metrics">
          <div className="metric">
            <span className="metric-label">Speed</span>
            <span className="metric-value">{motorState.speed.toFixed(0)} px/s</span>
            <div className="metric-bar" style={{ width: `${Math.min(motorState.speed / 10, 100)}%` }} />
          </div>
          <div className="metric">
            <span className="metric-label">Jerk</span>
            <span className="metric-value">{motorState.jerk.toFixed(0)} px/s²</span>
            <div className="metric-bar metric-bar--jerk" style={{ width: `${Math.min(motorState.jerk / 100, 100)}%` }} />
          </div>
          <div className="metric">
            <span className="metric-label">Velocity X</span>
            <span className="metric-value">{motorState.velocity.x.toFixed(0)}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Velocity Y</span>
            <span className="metric-value">{motorState.velocity.y.toFixed(0)}</span>
          </div>
        </div>
      </section>

      {/* Interactive Test Modules */}
      <section className="test-modules">
        <h2>Interactive Test Modules</h2>
        <p className="test-instructions">
          Hover, click, and scroll to generate events. Check the browser console for telemetry batches.
        </p>
        
        <div className="module-grid">
          {/* Module A - Base Style */}
          <div 
            className="test-module test-module--base"
            data-module-id="module_A"
            data-module-type="product-card"
            data-module-genre="base"
            data-module-loud="false"
          >
            <div className="module-image"></div>
            <h3>Base Style Card</h3>
            <p>Neutral, clean aesthetic</p>
            <button data-track-id="cta_base">Shop Now</button>
          </div>

          {/* Module B - Minimalist Style */}
          <div 
            className="test-module test-module--minimalist"
            data-module-id="module_B"
            data-module-type="product-card"
            data-module-genre="minimalist"
            data-module-loud="false"
          >
            <div className="module-image"></div>
            <h3>Minimalist Card</h3>
            <p>Clean typography, whitespace</p>
            <button data-track-id="cta_minimalist">Explore</button>
          </div>

          {/* Module C - Neobrutalist Style (LOUD) */}
          <div 
            className="test-module test-module--neobrutalist"
            data-module-id="module_C"
            data-module-type="product-card"
            data-module-genre="neobrutalist"
            data-module-loud="true"
          >
            <div className="module-image"></div>
            <h3>NEOBRUTALIST</h3>
            <p>Bold, raw aesthetic</p>
            <button data-track-id="cta_neo">BUY NOW</button>
          </div>

          {/* Module D - Glassmorphism Style */}
          <div 
            className="test-module test-module--glassmorphism"
            data-module-id="module_D"
            data-module-type="product-card"
            data-module-genre="glassmorphism"
            data-module-loud="false"
          >
            <div className="module-image"></div>
            <h3>Glass Card</h3>
            <p>Blur effects, transparency</p>
            <button data-track-id="cta_glass">View Details</button>
          </div>

          {/* Module E - LOUD A/B Test */}
          <div 
            className="test-module test-module--loud"
            data-module-id="module_E"
            data-module-type="cta"
            data-module-genre="loud"
            data-module-loud="true"
          >
            <div className="loud-badge">A/B TEST</div>
            <h3>🔥 LOUD MODULE 🔥</h3>
            <p>High-contrast test variant</p>
            <button data-track-id="cta_loud">TAKE ACTION</button>
          </div>

          {/* Module F - Another Base for comparison */}
          <div 
            className="test-module test-module--base"
            data-module-id="module_F"
            data-module-type="product-card"
            data-module-genre="base"
            data-module-loud="false"
          >
            <div className="module-image"></div>
            <h3>Another Base Card</h3>
            <p>Control variant</p>
            <button data-track-id="cta_base_2">Learn More</button>
          </div>
        </div>
      </section>

      {/* Scroll Test Section */}
      <section className="scroll-test">
        <h2>Scroll Test Section</h2>
        <p>Scroll through this area to test scroll tracking and dwell time detection.</p>
        
        <div className="scroll-content">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div 
              key={i}
              className="scroll-item"
              data-module-id={`scroll_item_${i}`}
              data-module-type="content-block"
              data-module-genre="base"
              data-module-loud={i === 4 ? 'true' : 'false'}
            >
              <h4>Content Block #{i}</h4>
              {i === 4 && <span className="loud-indicator">LOUD</span>}
              <p>This is a scrollable content block for testing viewport enter/leave events.</p>
            </div>
          ))}
        </div>
      </section>

      {/* Console Instructions */}
      <footer className="demo-footer">
        <h3>📋 How to Test</h3>
        <ol>
          <li>Open your browser's Developer Console (F12 → Console)</li>
          <li>Move your mouse around to see motor state changes</li>
          <li>Hover over modules to trigger hover events</li>
          <li>Click buttons to trigger click events</li>
          <li>Scroll to trigger viewport and scroll events</li>
          <li>Wait 5 seconds to see batched telemetry logs</li>
        </ol>
      </footer>
    </div>
  );
}
