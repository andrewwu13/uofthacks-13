/**
 * Mouse Tracker
 * Captures mouse position, velocity, and acceleration for motor telemetry
 */

import type { MotorSample } from './types';

export interface MouseTrackerConfig {
  sampleInterval: number;  // ms between samples (default: 16ms ~60fps)
  bufferSize: number;      // Max samples before auto-flush
  onFlush: (samples: MotorSample[], t0: number, dt: number) => void;
}

export class MouseTracker {
  private config: MouseTrackerConfig;
  private samples: MotorSample[] = [];
  private t0: number = 0;
  private lastSampleTime: number = 0;
  private isTracking: boolean = false;
  private lastPosition: MotorSample | null = null;
  
  // Computed derivatives
  private velocity: { x: number; y: number } = { x: 0, y: 0 };
  private acceleration: { x: number; y: number } = { x: 0, y: 0 };

  constructor(config: Partial<MouseTrackerConfig> & Pick<MouseTrackerConfig, 'onFlush'>) {
    this.config = {
      sampleInterval: 16,
      bufferSize: 60, // ~1 second at 60fps
      ...config,
    };
  }

  start(): void {
    if (this.isTracking) return;
    this.isTracking = true;
    this.samples = [];
    this.t0 = Date.now();
    
    document.addEventListener('mousemove', this.handleMouseMove);
    document.addEventListener('mouseenter', this.handleMouseEnter);
    document.addEventListener('mouseleave', this.handleMouseLeave);
    
    console.log('[MouseTracker] Started tracking');
  }

  stop(): void {
    if (!this.isTracking) return;
    this.isTracking = false;
    
    document.removeEventListener('mousemove', this.handleMouseMove);
    document.removeEventListener('mouseenter', this.handleMouseEnter);
    document.removeEventListener('mouseleave', this.handleMouseLeave);
    
    // Flush remaining samples
    this.flush();
    console.log('[MouseTracker] Stopped tracking');
  }

  private handleMouseMove = (e: MouseEvent): void => {
    const now = Date.now();
    
    // Throttle samples based on interval
    if (now - this.lastSampleTime < this.config.sampleInterval) {
      return;
    }
    
    const sample: MotorSample = { x: e.clientX, y: e.clientY };
    
    // Calculate derivatives if we have previous position
    if (this.lastPosition) {
      const dt = (now - this.lastSampleTime) / 1000; // seconds
      const prevVelocity = { ...this.velocity };
      
      // Velocity (pixels/second)
      this.velocity = {
        x: (sample.x - this.lastPosition.x) / dt,
        y: (sample.y - this.lastPosition.y) / dt,
      };
      
      // Acceleration (pixels/second²)
      this.acceleration = {
        x: (this.velocity.x - prevVelocity.x) / dt,
        y: (this.velocity.y - prevVelocity.y) / dt,
      };
    }
    
    this.lastPosition = sample;
    this.lastSampleTime = now;
    
    // Add to buffer
    if (this.samples.length === 0) {
      this.t0 = now;
    }
    this.samples.push(sample);
    
    // Auto-flush when buffer is full
    if (this.samples.length >= this.config.bufferSize) {
      this.flush();
    }
  };

  private handleMouseEnter = (): void => {
    // Reset tracking when mouse enters viewport
    this.lastPosition = null;
    this.velocity = { x: 0, y: 0 };
    this.acceleration = { x: 0, y: 0 };
  };

  private handleMouseLeave = (): void => {
    // Flush when mouse leaves viewport
    this.flush();
  };

  flush(): void {
    if (this.samples.length === 0) return;
    
    this.config.onFlush(
      [...this.samples],
      this.t0,
      this.config.sampleInterval
    );
    
    this.samples = [];
  }

  getVelocity(): { x: number; y: number } {
    return { ...this.velocity };
  }

  getAcceleration(): { x: number; y: number } {
    return { ...this.acceleration };
  }

  getSpeed(): number {
    return Math.sqrt(this.velocity.x ** 2 + this.velocity.y ** 2);
  }

  /**
   * Compute "jerkiness" - high-frequency changes in acceleration
   * Used to detect anxious/indecisive behavior
   */
  getJerk(): number {
    return Math.sqrt(this.acceleration.x ** 2 + this.acceleration.y ** 2);
  }
}
