/**
 * Interaction Tracker
 * Tracks clicks, hovers, and focus events on UI elements
 */

import type { TelemetryEvent } from './types';

export interface InteractionTrackerConfig {
  hoverThreshold: number;  // ms before hover is considered significant (default: 200)
  onEvent: (event: TelemetryEvent) => void;
}

interface HoverState {
  targetId: string;
  startTime: number;
  element: Element;
}

export class InteractionTracker {
  private config: InteractionTrackerConfig;
  private isTracking: boolean = false;
  private activeHovers: Map<string, HoverState> = new Map();
  private activeFocus: Map<string, number> = new Map();
  private selectionTimeout: number | null = null;

  constructor(config: Partial<InteractionTrackerConfig> & Pick<InteractionTrackerConfig, 'onEvent'>) {
    this.config = {
      hoverThreshold: 200,
      ...config,
    };
  }

  start(): void {
    if (this.isTracking) return;
    this.isTracking = true;

    document.addEventListener('click', this.handleClick, { capture: true });
    document.addEventListener('mouseenter', this.handleMouseEnter, { capture: true });
    document.addEventListener('mouseleave', this.handleMouseLeave, { capture: true });
    document.addEventListener('focusin', this.handleFocus, { capture: true });
    document.addEventListener('focusout', this.handleBlur, { capture: true });
    document.addEventListener('selectionchange', this.handleSelectionChange);

    console.log('[InteractionTracker] Started tracking');
  }

  stop(): void {
    if (!this.isTracking) return;
    this.isTracking = false;

    document.removeEventListener('click', this.handleClick, { capture: true });
    document.removeEventListener('mouseenter', this.handleMouseEnter, { capture: true });
    document.removeEventListener('mouseleave', this.handleMouseLeave, { capture: true });
    document.removeEventListener('focusin', this.handleFocus, { capture: true });
    document.removeEventListener('focusout', this.handleBlur, { capture: true });
    document.removeEventListener('selectionchange', this.handleSelectionChange);

    if (this.selectionTimeout) clearTimeout(this.selectionTimeout);

    console.log('[InteractionTracker] Stopped tracking');
  }

  private findTrackableParent(element: Element | null): Element | null {
    while (element) {
      // Guard: Make sure element is actually an Element with hasAttribute
      if (!element || typeof element.hasAttribute !== 'function') {
        return null;
      }

      if (
        element.hasAttribute('data-module-id') ||
        element.hasAttribute('data-track-id') ||
        element.hasAttribute('data-track-context') ||
        element.tagName === 'A' ||
        element.tagName === 'BUTTON'
      ) {
        return element;
      }
      element = element.parentElement;
    }
    return null;
  }

  private getTargetId(element: Element): string {
    return (
      element.getAttribute('data-module-id') ||
      element.getAttribute('data-track-id') ||
      element.getAttribute('id') ||
      `${element.tagName.toLowerCase()}_${element.className.split(' ')[0] || 'unknown'}`
    );
  }

  private getElementMetadata(element: Element): Record<string, unknown> {
    // Find nearest template ID by traversing up
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
      tag_name: element.tagName.toLowerCase(),
      class_name: element.className,
      track_context: element.getAttribute('data-track-context'),
    };
  }

  private handleClick = (e: MouseEvent): void => {
    const target = this.findTrackableParent(e.target as Element);
    if (!target) return;

    this.config.onEvent({
      ts: Math.floor(Date.now() / 1000),
      type: 'click',
      target_id: this.getTargetId(target),
      position: { x: e.clientX, y: e.clientY },
      metadata: this.getElementMetadata(target),
    });
  };

  private handleMouseEnter = (e: MouseEvent): void => {
    const target = this.findTrackableParent(e.target as Element);
    if (!target) return;

    const targetId = this.getTargetId(target);
    const now = Date.now();

    // Track hover start
    this.activeHovers.set(targetId, {
      targetId,
      startTime: now,
      element: target,
    });

    this.config.onEvent({
      ts: Math.floor(now / 1000),
      type: 'hover-enter',
      target_id: targetId,
      position: { x: e.clientX, y: e.clientY },
      metadata: this.getElementMetadata(target),
    });
  };

  private handleMouseLeave = (e: MouseEvent): void => {
    const target = this.findTrackableParent(e.target as Element);
    if (!target) return;

    const targetId = this.getTargetId(target);
    const hoverState = this.activeHovers.get(targetId);
    let hoverDuration: number | undefined;

    if (hoverState) {
      hoverDuration = Date.now() - hoverState.startTime;

      // Only emit if hover was significant
      if (hoverDuration >= this.config.hoverThreshold) {
        this.config.onEvent({
          ts: Math.floor(Date.now() / 1000),
          type: 'hover',
          target_id: targetId,
          duration_ms: hoverDuration,
          metadata: this.getElementMetadata(target),
        });
      }

      this.activeHovers.delete(targetId);
    }

    this.config.onEvent({
      ts: Math.floor(Date.now() / 1000),
      type: 'hover-leave',
      target_id: targetId,
      duration_ms: hoverDuration,
      metadata: this.getElementMetadata(target),
    });
  };

  private handleFocus = (e: FocusEvent): void => {
    const target = this.findTrackableParent(e.target as Element);
    if (!target) return;

    const targetId = this.getTargetId(target);
    this.activeFocus.set(targetId, Date.now());

    this.config.onEvent({
      ts: Math.floor(Date.now() / 1000),
      type: 'focus',
      target_id: targetId,
      metadata: this.getElementMetadata(target),
    });
  };

  private handleBlur = (e: FocusEvent): void => {
    const target = this.findTrackableParent(e.target as Element);
    if (!target) return;

    const targetId = this.getTargetId(target);
    const focusStartTime = this.activeFocus.get(targetId);
    let focusDuration: number | undefined;

    if (focusStartTime) {
      focusDuration = Date.now() - focusStartTime;
      this.activeFocus.delete(targetId);
    }

    this.config.onEvent({
      ts: Math.floor(Date.now() / 1000),
      type: 'blur',
      target_id: targetId,
      duration_ms: focusDuration,
      metadata: this.getElementMetadata(target),
    });
  };

  private handleSelectionChange = (): void => {
    if (this.selectionTimeout) {
      clearTimeout(this.selectionTimeout);
    }

    // Debounce to wait for user to finish selecting
    this.selectionTimeout = window.setTimeout(() => {
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed) return;

      const selectedText = selection.toString().trim();
      if (!selectedText) return;

      const anchorNode = selection.anchorNode;
      if (!anchorNode) return;

      const targetRaw = anchorNode.nodeType === Node.ELEMENT_NODE
        ? (anchorNode as Element)
        : anchorNode.parentElement;

      if (!targetRaw) return;

      const target = this.findTrackableParent(targetRaw);
      if (!target) return;

      this.config.onEvent({
        ts: Math.floor(Date.now() / 1000),
        type: 'text_select',
        target_id: this.getTargetId(target),
        metadata: {
          ...this.getElementMetadata(target),
          selected_text: selectedText.substring(0, 500), // truncate just in case
          selection_length: selectedText.length,
        },
      });
    }, 500); // 500ms debounce
  };
}
