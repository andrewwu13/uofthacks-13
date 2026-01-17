/**
 * Telemetry Types
 * Matches backend models from app/models/events.py
 */

/** Motor telemetry sample - compact position data */
export interface MotorSample {
  x: number;
  y: number;
}

/** Motor telemetry payload for POST /telemetry/motor */
export interface MotorTelemetryPayload {
  session_id: string;
  device: 'mouse' | 'touch';
  t0: number;        // Unix timestamp of first sample
  dt: number;        // Milliseconds between samples
  samples: [number, number][]; // [[x, y], ...]
}

/** Interaction event types */
export type EventType = 
  | 'click'
  | 'hover'
  | 'hover-enter'
  | 'hover-leave'
  | 'enter_viewport'
  | 'leave_viewport'
  | 'focus'
  | 'blur'
  | 'scroll_stop';

/** Single telemetry event */
export interface TelemetryEvent {
  ts: number;           // Unix timestamp
  type: EventType;
  target_id: string;    // Module ID or element identifier
  duration_ms?: number; // For hover events
  position?: { x: number; y: number };
  metadata?: Record<string, unknown>;
}

/** Events telemetry payload for POST /telemetry/events */
export interface EventsTelemetryPayload {
  session_id: string;
  events: TelemetryEvent[];
}

/** Device type detection */
export type DeviceType = 'desktop' | 'mobile' | 'tablet';

/** Batch payload combining motor and events */
export interface TelemetryBatch {
  session_id: string;
  device_type: DeviceType;
  timestamp: number;
  motor?: MotorTelemetryPayload;
  events: TelemetryEvent[];
}
