"use client";

import { useEffect, useState } from "react";

interface PipelineEvent {
  event: string;
  data: Record<string, unknown>;
}

interface PageStatus {
  id: string;
  module: string;
  migration_status: string;
  current_step: number;
  total_cost: number;
}

export default function Dashboard() {
  const [pages, setPages] = useState<PageStatus[]>([]);
  const [events, setEvents] = useState<PipelineEvent[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/api/pages")
      .then((r) => r.json())
      .then((d) => setPages(d.data || []))
      .catch(() => {});

    const ws = new WebSocket("ws://localhost:8000/ws");
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      setEvents((prev) => [msg, ...prev].slice(0, 50));
    };

    return () => ws.close();
  }, []);

  return (
    <div style={{ padding: 32, maxWidth: 1200, margin: "0 auto" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 32 }}>
        <h1 style={{ fontSize: 20, fontWeight: 700 }}>Silicon2 Migration</h1>
        <span
          style={{
            width: 8, height: 8, borderRadius: "50%",
            background: connected ? "#10b981" : "#ef4444",
          }}
        />
        <span style={{ fontSize: 11, color: "#71717a" }}>
          {connected ? "Connected" : "Disconnected"}
        </span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Pages table */}
        <div style={{ background: "#111113", border: "1px solid #27272a", borderRadius: 8, padding: 16 }}>
          <h2 style={{ fontSize: 13, fontWeight: 600, marginBottom: 12 }}>Pages ({pages.length})</h2>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
            <thead>
              <tr style={{ color: "#71717a", textAlign: "left" }}>
                <th style={{ padding: "6px 8px" }}>ID</th>
                <th style={{ padding: "6px 8px" }}>Status</th>
                <th style={{ padding: "6px 8px" }}>Step</th>
                <th style={{ padding: "6px 8px" }}>Cost</th>
              </tr>
            </thead>
            <tbody>
              {pages.map((p) => (
                <tr key={p.id} style={{ borderTop: "1px solid #1e1e21" }}>
                  <td style={{ padding: "6px 8px", fontFamily: "monospace" }}>{p.id}</td>
                  <td style={{ padding: "6px 8px" }}>{p.migration_status}</td>
                  <td style={{ padding: "6px 8px" }}>{p.current_step}/9</td>
                  <td style={{ padding: "6px 8px" }}>${p.total_cost?.toFixed(3)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Live events */}
        <div style={{ background: "#111113", border: "1px solid #27272a", borderRadius: 8, padding: 16 }}>
          <h2 style={{ fontSize: 13, fontWeight: 600, marginBottom: 12 }}>Live Events</h2>
          <div style={{ maxHeight: 400, overflowY: "auto" }}>
            {events.length === 0 && (
              <p style={{ color: "#71717a", fontSize: 11 }}>Waiting for pipeline events...</p>
            )}
            {events.map((ev, i) => (
              <div
                key={i}
                style={{
                  padding: "6px 8px", marginBottom: 4, fontSize: 11,
                  background: "#18181b", borderRadius: 4, fontFamily: "monospace",
                }}
              >
                <span style={{ color: "#3b82f6" }}>{ev.event}</span>{" "}
                <span style={{ color: "#a1a1aa" }}>{JSON.stringify(ev.data)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
