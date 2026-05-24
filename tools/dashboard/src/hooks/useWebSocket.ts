"use client";

import { useEffect, useRef, useState, useCallback } from "react";

interface PipelineEvent {
  event: string;
  data: Record<string, unknown>;
}

export function useWebSocket(url?: string) {
  const wsUrl = url || "ws://localhost:8000/ws";
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState<PipelineEvent[]>([]);

  useEffect(() => {
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);
    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        setEvents((prev) => [msg, ...prev].slice(0, 100));
      } catch {}
    };

    return () => {
      ws.close();
    };
  }, [wsUrl]);

  const clearEvents = useCallback(() => setEvents([]), []);

  return { connected, events, clearEvents };
}
