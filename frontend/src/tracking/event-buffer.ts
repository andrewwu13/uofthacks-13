/**
 * Event Buffer
 * Batches telemetry events and flushes them at intervals
 */

import type { TelemetryEvent, MotorSample, TelemetryBatch, DeviceType } from './types';

export interface EventBufferConfig {
  flushInterval: number;    // ms between automatic flushes (default: 5000)
  maxEvents: number;        // Max events before auto-flush (default: 100)
  sessionId: string;
  deviceType: DeviceType;
  onFlush: (batch: TelemetryBatch) => void;
}

export class EventBuffer {
  private config: EventBufferConfig;
  private events: TelemetryEvent[] = [];
  private motorSamples: MotorSample[] = [];
  private motorT0: number = 0;
  private motorDt: number = 16;
  private flushTimer: ReturnType<typeof setInterval> | null = null;

  constructor(config: EventBufferConfig) {
    this.config = config;
  }

  start(): void {
    if (this.flushTimer) return;
    
    this.flushTimer = setInterval(() => {
      this.flush();
    }, this.config.flushInterval);
    
    console.log(`[EventBuffer] Started with ${this.config.flushInterval}ms flush interval`);
  }

  stop(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }
    
    // Final flush
    this.flush();
    console.log('[EventBuffer] Stopped');
  }

  addEvent(event: TelemetryEvent): void {
    this.events.push(event);
    
    // Auto-flush if buffer is full
    if (this.events.length >= this.config.maxEvents) {
      this.flush();
    }
  }

  addMotorSamples(samples: MotorSample[], t0: number, dt: number): void {
    if (this.motorSamples.length === 0) {
      this.motorT0 = t0;
      this.motorDt = dt;
    }
    this.motorSamples.push(...samples);
  }

  flush(): void {
    // Skip if nothing to send
    if (this.events.length === 0 && this.motorSamples.length === 0) {
      return;
    }

    const batch: TelemetryBatch = {
      session_id: this.config.sessionId,
      device_type: this.config.deviceType,
      timestamp: Math.floor(Date.now() / 1000),
      events: [...this.events],
    };

    // Add motor data if present
    if (this.motorSamples.length > 0) {
      batch.motor = {
        session_id: this.config.sessionId,
        device: 'mouse',
        t0: this.motorT0,
        dt: this.motorDt,
        samples: this.motorSamples.map(s => [s.x, s.y] as [number, number]),
      };
    }

    // Clear buffers
    this.events = [];
    this.motorSamples = [];

    // Emit batch
    this.config.onFlush(batch);
  }

  getEventCount(): number {
    return this.events.length;
  }

  getMotorSampleCount(): number {
    return this.motorSamples.length;
  }
}
