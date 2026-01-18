/**
 * SSE Hook for receiving layout updates from backend
 * Connects to /stream/{session_id} and listens for layout:update events
 */

import { useEffect, useRef, useState, useCallback } from 'react';

// Backend API URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface LayoutUpdate {
  layout_id: string;
  layout_hash: string;
  components: Array<{
    id: string;
    type: string;
    variant: string;
    genre: string;
    props: Record<string, unknown>;
  }>;
  tokens: {
    theme: string;
    border_radius: string;
    font_weight: string;
    density: string;
    accent_color: string;
  };
  metadata: Record<string, unknown>;
}

export interface UseSSELayoutOptions {
  sessionId: string | null;
  onLayoutUpdate?: (layout: LayoutUpdate) => void;
  enabled?: boolean;
}

export interface UseSSELayoutResult {
  isConnected: boolean;
  lastLayout: LayoutUpdate | null;
  updateCount: number;
  error: string | null;
  reconnect: () => void;
}

/**
 * Hook to subscribe to SSE layout updates
 */
export function useSSELayout({
  sessionId,
  onLayoutUpdate,
  enabled = true
}: UseSSELayoutOptions): UseSSELayoutResult {
  const [isConnected, setIsConnected] = useState(false);
  const [lastLayout, setLastLayout] = useState<LayoutUpdate | null>(null);
  const [updateCount, setUpdateCount] = useState(0);
  const [error, setError] = useState<string | null>(null);
  
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (!sessionId || !enabled) return;
    
    // Clean up existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    const url = `${API_BASE_URL}/stream/${sessionId}`;
    console.log('[SSE] Connecting to:', url);
    
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      console.log('[SSE] Connected');
      setIsConnected(true);
      setError(null);
    };

    // Listen for layout:update events
    eventSource.addEventListener('layout:update', (event) => {
      try {
        const layout = JSON.parse(event.data) as LayoutUpdate;
        console.log('[SSE] Layout update received:', layout.layout_id);
        
        setLastLayout(layout);
        setUpdateCount(prev => prev + 1);
        
        if (onLayoutUpdate) {
          onLayoutUpdate(layout);
        }
      } catch (err) {
        console.error('[SSE] Failed to parse layout update:', err);
      }
    });

    eventSource.onerror = (err) => {
      console.error('[SSE] Connection error:', err);
      setIsConnected(false);
      setError('SSE connection error');
      
      // Auto-reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        console.log('[SSE] Attempting reconnect...');
        connect();
      }, 3000);
    };

  }, [sessionId, enabled, onLayoutUpdate]);

  // Connect when session ID is available
  useEffect(() => {
    if (sessionId && enabled) {
      connect();
    }

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [sessionId, enabled, connect]);

  const reconnect = useCallback(() => {
    connect();
  }, [connect]);

  return {
    isConnected,
    lastLayout,
    updateCount,
    error,
    reconnect
  };
}

export default useSSELayout;
