/**
 * Scroll Tracker
 * Tracks scroll position, velocity, direction, and dwell time
 */

import type { TelemetryEvent } from './types';

export interface ScrollTrackerConfig {
  dwellThreshold: number;     // ms of no scroll to consider "dwell" (default: 500)
  scrollStopDelay: number;    // ms after scroll stops to emit event (default: 150)
  onEvent: (event: TelemetryEvent) => void;
}

export class ScrollTracker {
  private config: ScrollTrackerConfig;
  private isTracking: boolean = false;

  private lastScrollY: number = 0;
  private lastScrollTime: number = 0;
  private scrollVelocity: number = 0;
  private scrollDirection: 'up' | 'down' | 'none' = 'none';

  private scrollStopTimer: ReturnType<typeof setTimeout> | null = null;
  private dwellStartTime: number = 0;
  private currentViewportModules: Set<string> = new Set();

  private moduleEntryTimes: Map<string, number> = new Map();
  private lastModuleLeft: { id: string, time: number } | null = null;

  constructor(config: Partial<ScrollTrackerConfig> & Pick<ScrollTrackerConfig, 'onEvent'>) {
    this.config = {
      dwellThreshold: 500,
      scrollStopDelay: 150,
      ...config,
    };
  }

  start(): void {
    if (this.isTracking) return;
    this.isTracking = true;
    this.lastScrollY = window.scrollY;
    this.lastScrollTime = Date.now();

    window.addEventListener('scroll', this.handleScroll, { passive: true });

    // Set up IntersectionObserver for viewport tracking
    this.setupViewportObserver();

    console.log('[ScrollTracker] Started tracking');
  }

  stop(): void {
    if (!this.isTracking) return;
    this.isTracking = false;

    window.removeEventListener('scroll', this.handleScroll);

    if (this.scrollStopTimer) {
      clearTimeout(this.scrollStopTimer);
    }

    console.log('[ScrollTracker] Stopped tracking');
  }

  private handleScroll = (): void => {
    const now = Date.now();
    const currentY = window.scrollY;
    // Prevent division by zero if updates happen too fast
    const dt = Math.max((now - this.lastScrollTime) / 1000, 0.001);

    // Calculate velocity and direction
    const deltaY = currentY - this.lastScrollY;
    const velocity = Math.abs(deltaY) / dt;
    this.scrollVelocity = velocity;
    this.scrollDirection = deltaY > 0 ? 'down' : deltaY < 0 ? 'up' : 'none';

    // Excessive Scrolling Detection
    // High velocity without stopping (e.g. searching for something)
    if (velocity > 5000) { // Threshold for "frantic" scrolling (increased to reduce sensitivity)
      this.config.onEvent({
        ts: Math.floor(now / 1000),
        type: 'excessive_scroll',
        target_id: 'viewport',
        metadata: {
          velocity,
          direction: this.scrollDirection,
          scroll_percent: this.getScrollPercent()
        }
      });
    }

    this.lastScrollY = currentY;
    this.lastScrollTime = now;

    // Reset dwell timer
    this.dwellStartTime = now;

    // Set up scroll stop detection
    if (this.scrollStopTimer) {
      clearTimeout(this.scrollStopTimer);
    }

    this.scrollStopTimer = setTimeout(() => {
      this.handleScrollStop();
    }, this.config.scrollStopDelay);
  };

  private handleScrollStop(): void {
    const now = Date.now();
    const dwellTime = now - this.dwellStartTime;

    // Emit scroll_stop event if dwell exceeds threshold
    if (dwellTime >= this.config.dwellThreshold) {
      this.config.onEvent({
        ts: Math.floor(now / 1000),
        type: 'scroll_stop',
        target_id: 'viewport',
        duration_ms: dwellTime,
        metadata: {
          scroll_y: this.lastScrollY,
          scroll_percent: this.getScrollPercent(),
          direction: this.scrollDirection,
          velocity: this.scrollVelocity,
        },
      });
    }

    this.scrollVelocity = 0;
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

  private setupViewportObserver(): void {
    const observer = new IntersectionObserver(
      (entries) => {
        const now = Date.now();
        const nowSec = Math.floor(now / 1000);

        entries.forEach((entry) => {
          const moduleId = entry.target.getAttribute('data-module-id');
          if (!moduleId) return;

          if (entry.isIntersecting) {
            if (!this.currentViewportModules.has(moduleId)) {
              this.currentViewportModules.add(moduleId);
              this.moduleEntryTimes.set(moduleId, now);

              const metadata = this.getElementMetadata(entry.target);

              this.config.onEvent({
                ts: nowSec,
                type: 'enter_viewport',
                target_id: moduleId,
                metadata,
              });

              // Check for module transition (flick)
              if (this.lastModuleLeft && (now - this.lastModuleLeft.time < 500) && this.scrollVelocity > 1000) {
                this.config.onEvent({
                  ts: nowSec,
                  type: 'module_transition',
                  target_id: moduleId,
                  duration_ms: now - this.lastModuleLeft.time,
                  metadata: {
                    ...metadata,
                    from_module_id: this.lastModuleLeft.id,
                    to_module_id: moduleId,
                    velocity: this.scrollVelocity
                  }
                });
              }
            }
          } else {
            if (this.currentViewportModules.has(moduleId)) {
              this.currentViewportModules.delete(moduleId);
              this.lastModuleLeft = { id: moduleId, time: now };

              const entryTime = this.moduleEntryTimes.get(moduleId);
              const duration_ms = entryTime ? (now - entryTime) : undefined;
              if (entryTime) this.moduleEntryTimes.delete(moduleId);

              this.config.onEvent({
                ts: nowSec,
                type: 'leave_viewport',
                target_id: moduleId,
                duration_ms,
                metadata: this.getElementMetadata(entry.target),
              });
            }
          }
        });
      },
      {
        threshold: [0, 0.25, 0.5, 0.75, 1],
        rootMargin: '0px',
      }
    );

    // Observe all layout modules
    document.querySelectorAll('[data-module-id]').forEach((el) => {
      observer.observe(el);
    });

    // Re-observe when DOM changes
    const mutationObserver = new MutationObserver(() => {
      document.querySelectorAll('[data-module-id]').forEach((el) => {
        observer.observe(el);
      });
    });

    mutationObserver.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }

  getScrollPercent(): number {
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    return docHeight > 0 ? (window.scrollY / docHeight) * 100 : 0;
  }

  getVelocity(): number {
    return this.scrollVelocity;
  }

  getDirection(): 'up' | 'down' | 'none' {
    return this.scrollDirection;
  }
}
