/**
 * Telemetry Manager
 * Central coordinator for all tracking subsystems
 */

import { MouseTracker } from './mouse-tracker';
import { ScrollTracker } from './scroll-tracker';
import { InteractionTracker } from './interaction-tracker';
import { EventBuffer } from './event-buffer';
import type { TelemetryEvent, TelemetryBatch, DeviceType } from './types';

export interface TelemetryManagerConfig {
  sessionId?: string;
  flushInterval?: number;
  enableConsoleLog?: boolean;
  onBatch?: (batch: TelemetryBatch) => void;
}

/**
 * Detect device type based on user agent and touch support
 */
function detectDeviceType(): DeviceType {
  const ua = navigator.userAgent.toLowerCase();
  const hasTouchScreen = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  
  if (/tablet|ipad|playbook|silk/.test(ua) || (hasTouchScreen && window.innerWidth >= 768)) {
    return 'tablet';
  }
  if (/mobile|iphone|ipod|android|blackberry|opera mini|iemobile/.test(ua) || (hasTouchScreen && window.innerWidth < 768)) {
    return 'mobile';
  }
  return 'desktop';
}

/**
 * Generate a session ID
 */
function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
}

export class TelemetryManager {
  private config: Required<TelemetryManagerConfig>;
  private mouseTracker: MouseTracker;
  private scrollTracker: ScrollTracker;
  private interactionTracker: InteractionTracker;
  private eventBuffer: EventBuffer;
  private isRunning: boolean = false;
  private batchCount: number = 0;

  constructor(config: TelemetryManagerConfig = {}) {
    this.config = {
      sessionId: config.sessionId || generateSessionId(),
      flushInterval: config.flushInterval || 5000,
      enableConsoleLog: config.enableConsoleLog ?? true,
      onBatch: config.onBatch || (() => {}),
    };

    const deviceType = detectDeviceType();

    // Initialize event buffer
    this.eventBuffer = new EventBuffer({
      flushInterval: this.config.flushInterval,
      maxEvents: 100,
      sessionId: this.config.sessionId,
      deviceType,
      onFlush: (batch) => this.handleBatchFlush(batch),
    });

    // Initialize trackers
    this.mouseTracker = new MouseTracker({
      sampleInterval: 16,
      bufferSize: 60,
      onFlush: (samples, t0, dt) => {
        this.eventBuffer.addMotorSamples(samples, t0, dt);
      },
    });

    this.scrollTracker = new ScrollTracker({
      dwellThreshold: 500,
      scrollStopDelay: 150,
      onEvent: (event) => this.addEvent(event),
    });

    this.interactionTracker = new InteractionTracker({
      hoverThreshold: 200,
      onEvent: (event) => this.addEvent(event),
    });
  }

  start(): void {
    if (this.isRunning) return;
    this.isRunning = true;

    console.log(`[TelemetryManager] Starting with session: ${this.config.sessionId}`);

    this.eventBuffer.start();
    this.mouseTracker.start();
    this.scrollTracker.start();
    this.interactionTracker.start();
  }

  stop(): void {
    if (!this.isRunning) return;
    this.isRunning = false;

    console.log('[TelemetryManager] Stopping...');

    this.mouseTracker.stop();
    this.scrollTracker.stop();
    this.interactionTracker.stop();
    this.eventBuffer.stop();
  }

  private addEvent(event: TelemetryEvent): void {
    this.eventBuffer.addEvent(event);
    
    if (this.config.enableConsoleLog) {
      console.log(`[Telemetry] ${event.type}:`, event);
    }
  }

  private handleBatchFlush(batch: TelemetryBatch): void {
    this.batchCount++;
    
    if (this.config.enableConsoleLog) {
      console.group(`[TelemetryManager] Batch #${this.batchCount} flushed`);
      console.log('Session ID:', batch.session_id);
      console.log('Device Type:', batch.device_type);
      console.log('Timestamp:', new Date(batch.timestamp * 1000).toISOString());
      console.log('Events:', batch.events.length);
      
      if (batch.motor) {
        console.log('Motor Samples:', batch.motor.samples.length);
      }
      
      // Log event breakdown
      const eventTypes = batch.events.reduce((acc, e) => {
        acc[e.type] = (acc[e.type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);
      console.log('Event Breakdown:', eventTypes);
      
      console.log('Full Batch:', batch);
      console.groupEnd();
    }

    // Call external handler
    this.config.onBatch(batch);
  }

  getSessionId(): string {
    return this.config.sessionId;
  }

  getBatchCount(): number {
    return this.batchCount;
  }

  /**
   * Get current motor state for real-time UI feedback
   */
  getMotorState(): { velocity: { x: number; y: number }; acceleration: { x: number; y: number }; speed: number; jerk: number } {
    return {
      velocity: this.mouseTracker.getVelocity(),
      acceleration: this.mouseTracker.getAcceleration(),
      speed: this.mouseTracker.getSpeed(),
      jerk: this.mouseTracker.getJerk(),
    };
  }
}

// Export singleton for easy access
let _instance: TelemetryManager | null = null;

export function getTelemetryManager(): TelemetryManager {
  if (!_instance) {
    _instance = new TelemetryManager();
  }
  return _instance;
}

export function initTelemetry(config?: TelemetryManagerConfig): TelemetryManager {
  if (_instance) {
    _instance.stop();
  }
  _instance = new TelemetryManager(config);
  _instance.start();
  return _instance;
}
