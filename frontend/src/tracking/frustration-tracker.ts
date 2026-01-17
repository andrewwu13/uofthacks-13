/**
 * Frustration Tracker
 * Detects patterns indicating user frustration:
 * - Click rage (repeated clicks)
 * - Dead clicks (clicking non-interactive elements)
 * - Click errors (clicks causing JS errors)
 */

import type { TelemetryEvent } from './types';

export interface FrustrationTrackerConfig {
  rageClickThreshold: number; // Max clicks to consider rage (default: 3)
  rageClickTimeWindow: number; // Time window for rage clicks in ms (default: 1000)
  onEvent: (event: TelemetryEvent) => void;
}

interface ClickState {
  targetId: string;
  count: number;
  firstClickTime: number;
  timer: ReturnType<typeof setTimeout> | null;
}

export class FrustrationTracker {
  private config: FrustrationTrackerConfig;
  private isTracking: boolean = false;
  private lastClickState: ClickState | null = null;
  private lastClickTime: number = 0;

  constructor(config: Partial<FrustrationTrackerConfig> & Pick<FrustrationTrackerConfig, 'onEvent'>) {
    this.config = {
      rageClickThreshold: 3,
      rageClickTimeWindow: 1000,
      ...config,
    };
  }

  start(): void {
    if (this.isTracking) return;
    this.isTracking = true;
    
    document.addEventListener('click', this.handleClick, { capture: true });
    window.addEventListener('error', this.handleError);
    window.addEventListener('unhandledrejection', this.handleRejection);
    document.addEventListener('visibilitychange', this.handleVisibilityChange);
    
    console.log('[FrustrationTracker] Started tracking');
  }

  stop(): void {
    if (!this.isTracking) return;
    this.isTracking = false;
    
    document.removeEventListener('click', this.handleClick, { capture: true });
    window.removeEventListener('error', this.handleError);
    window.removeEventListener('unhandledrejection', this.handleRejection);
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);
    
    if (this.lastClickState?.timer) {
      clearTimeout(this.lastClickState.timer);
    }
    
    console.log('[FrustrationTracker] Stopped tracking');
  }

  private getTargetId(element: Element): string {
    return (
      element.getAttribute('data-module-id') ||
      element.getAttribute('data-track-id') ||
      element.getAttribute('id') ||
      `${element.tagName.toLowerCase()}_${element.className.split(' ')[0] || 'unknown'}`
    );
  }

  private isInteracitve(element: Element): boolean {
    const tagName = element.tagName.toLowerCase();
    if (['a', 'button', 'input', 'select', 'textarea'].includes(tagName)) return true;
    if (element.hasAttribute('onclick')) return true;
    if (element.getAttribute('role') === 'button') return true;
    if (element.getAttribute('data-interactive') === 'true') return true;
    
    // Check computed style for pointer cursor
    try {
      const style = window.getComputedStyle(element);
      if (style.cursor === 'pointer') return true;
    } catch {
      // Ignore style check errors
    }
    
    return false;
  }

  private handleClick = (e: MouseEvent): void => {
    const target = e.target as Element;
    const now = Date.now();
    this.lastClickTime = now;
    
    // 1. Dead Click Detection
    // Check if clicking something that looks responsive but isn't
    // We filter out simple text selection clicks or background clicks
    if (!this.isInteracitve(target)) {
      // Basic heuristic: if it's not interactive but user clicked it
      // potentially misleading UI. 
      // We skip if it's just a container div without specific styling
      const style = window.getComputedStyle(target);
      if (style.cursor !== 'auto' && style.cursor !== 'default') {
         this.config.onEvent({
          ts: Math.floor(now / 1000),
          type: 'dead_click',
          target_id: this.getTargetId(target),
          metadata: {
            tag_name: target.tagName,
            cursor: style.cursor,
            text: target.textContent?.slice(0, 50)
          }
        });
      }
    }

    // 2. Click Rage Detection
    const targetId = this.getTargetId(target);
    
    if (this.lastClickState && this.lastClickState.targetId === targetId) {
      this.lastClickState.count++;
      
      const timeDiff = now - this.lastClickState.firstClickTime;
      
      if (timeDiff <= this.config.rageClickTimeWindow) {
        if (this.lastClickState.count === this.config.rageClickThreshold) {
          this.config.onEvent({
            ts: Math.floor(now / 1000),
            type: 'click_rage',
            target_id: targetId,
            metadata: {
              click_count: this.lastClickState.count,
              duration_ms: timeDiff
            }
          });
        }
      } else {
        // Reset if window expired
        this.resetClickState(targetId, now);
      }
    } else {
      // New target or first click
      this.resetClickState(targetId, now);
    }
  };

  private resetClickState(targetId: string, now: number): void {
    if (this.lastClickState?.timer) {
      clearTimeout(this.lastClickState.timer);
    }
    
    this.lastClickState = {
      targetId,
      count: 1,
      firstClickTime: now,
      timer: setTimeout(() => {
        this.lastClickState = null;
      }, this.config.rageClickTimeWindow)
    };
  }

  private handleError = (e: ErrorEvent): void => {
    this.checkClickError(e.message);
  };

  private handleRejection = (e: PromiseRejectionEvent): void => {
    this.checkClickError(String(e.reason));
  };

  private checkClickError(errorMessage: string): void {
    const now = Date.now();
    // If error happened within 100ms of a click, assume correlation
    if (now - this.lastClickTime < 100) {
      this.config.onEvent({
        ts: Math.floor(now / 1000),
        type: 'click_error',
        target_id: this.lastClickState?.targetId || 'unknown',
        metadata: {
          error: errorMessage
        }
      });
    }
  }

  private handleVisibilityChange = (): void => {
    this.config.onEvent({
      ts: Math.floor(Date.now() / 1000),
      type: 'visibility_change',
      target_id: 'document',
      metadata: {
        state: document.visibilityState
      }
    });
  }
}
