/**
 * Mouse Tracker
 * Captures mouse position, velocity, and acceleration for motor telemetry
 */

import type { MotorSample, TelemetryEvent } from './types';

export interface MouseTrackerConfig {
  sampleInterval: number;  // ms between samples (default: 16ms ~60fps)
  bufferSize: number;      // Max samples before auto-flush
  onFlush: (samples: MotorSample[], t0: number, dt: number) => void;
  onEvent?: (event: TelemetryEvent) => void;
}

export class MouseTracker {
  private config: MouseTrackerConfig;
  private samples: MotorSample[] = [];
  private t0: number = 0;
  private lastSampleTime: number = 0;
  private isTracking: boolean = false;
  private lastPosition: MotorSample | null = null;

  // Hesitation tracking state
  private hesitationStartTime: number = 0;
  private hesitationBox: { minX: number, maxX: number, minY: number, maxY: number } | null = null;

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

  private getElementMetadata(element: Element): Record<string, unknown> {
    let templateElement: Element | null = element;
    let templateId: string | null = null;
    while (templateElement && !templateId) {
      if (typeof templateElement.hasAttribute === 'function' && templateElement.hasAttribute('data-template-id')) {
        templateId = templateElement.getAttribute('data-template-id');
      }
      templateElement = templateElement.parentElement;
    }

    return {
      template_id: templateId ? parseInt(templateId, 10) : undefined,
      module_type: element.getAttribute('data-module-type'),
      module_genre: element.getAttribute('data-module-genre'),
      is_loud: element.getAttribute('data-module-loud') === 'true',
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

      // Hesitation Detection
      const jerk = this.getJerk();
      const speed = this.getSpeed();

      if (jerk > 800 && speed < 300) {
        if (!this.hesitationStartTime) {
          this.hesitationStartTime = now;
          this.hesitationBox = { minX: sample.x, maxX: sample.x, minY: sample.y, maxY: sample.y };
        } else if (this.hesitationBox) {
          this.hesitationBox.minX = Math.min(this.hesitationBox.minX, sample.x);
          this.hesitationBox.maxX = Math.max(this.hesitationBox.maxX, sample.x);
          this.hesitationBox.minY = Math.min(this.hesitationBox.minY, sample.y);
          this.hesitationBox.maxY = Math.max(this.hesitationBox.maxY, sample.y);

          const duration = now - this.hesitationStartTime;
          const boxWidth = this.hesitationBox.maxX - this.hesitationBox.minX;
          const boxHeight = this.hesitationBox.maxY - this.hesitationBox.minY;

          // If wiggling in a small area for > 400ms
          if (duration > 400 && boxWidth < 100 && boxHeight < 100 && this.config.onEvent) {
            const targetElement = document.elementFromPoint(sample.x, sample.y);
            let trackableParent = targetElement;
            while (trackableParent) {
              if (
                typeof trackableParent.hasAttribute === 'function' &&
                (trackableParent.hasAttribute('data-module-id') || trackableParent.hasAttribute('data-track-id'))
              ) {
                break;
              }
              trackableParent = trackableParent.parentElement;
            }

            if (trackableParent) {
              const targetId = trackableParent.getAttribute('data-module-id') ||
                trackableParent.getAttribute('data-track-id') || 'unknown';

              this.config.onEvent({
                ts: Math.floor(now / 1000),
                type: 'hesitation',
                target_id: targetId,
                position: { x: sample.x, y: sample.y },
                metadata: {
                  ...this.getElementMetadata(trackableParent),
                  jerk_metric: jerk,
                  bound_box_size: Math.max(boxWidth, boxHeight),
                  duration_ms: duration
                }
              });
            }

            // Reset to avoid spamming
            this.hesitationStartTime = 0;
            this.hesitationBox = null;
          }
        }
      } else {
        // Reset if they move fast or smooth out
        this.hesitationStartTime = 0;
        this.hesitationBox = null;
      }
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
