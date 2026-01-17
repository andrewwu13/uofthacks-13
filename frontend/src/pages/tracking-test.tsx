/**
 * Tracking Test Entry Point
 * Standalone entry for testing the telemetry tracking system
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import '../index.css';
import { TrackingDemo } from './TrackingDemo';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <TrackingDemo />
  </StrictMode>,
);
