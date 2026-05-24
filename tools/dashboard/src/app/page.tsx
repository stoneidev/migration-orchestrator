"use client";

import { useEffect, useState } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";
import { fetchPages } from "@/lib/api";

interface PageData {
  id: string;
  module: string;
  title: string;
  complexity: string;
  migration_status: string;
  current_step: number;
  total_cost: number;
}

export default function Dashboard() {
  const [pages, setPages] = useState<PageData[]>([]);
  const { connected, events } = useWebSocket();

  useEffect(() => {
    fetchPages().then(setPages).catch(() => {});
  }, []);

  const completed = pages.filter((p) => p.migration_status === "complete").length;
  const running = pages.filter((p) => p.migration_status === "running").length;
  const review = pages.filter((p) => p.migration_status === "review").length;
  const totalCost = pages.reduce((s, p) => s + (p.total_cost || 0), 0);

  return (
    <>
      <div className="header">
        <span style={{ fontSize: 12, color: "var(--text3)" }}>sk-main-php/adm / Dashboard</span>
        <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ width: 6, height: 6, borderRadius: "50%", background: connected ? "var(--green)" : "var(--red)" }} />
          <span style={{ fontSize: 10, color: "var(--text3)" }}>{connected ? "Live" : "Offline"}</span>
          <button className="btn btn-primary">Run Pipeline</button>
        </div>
      </div>
      <div className="content">
        {/* Metrics */}
        <div className="grid grid-5" style={{ marginBottom: 20 }}>
          <div className="metric">
            <div className="metric-label">Admin Pages</div>
            <div className="metric-value">1,099</div>
            <div className="metric-sub">specs: 707 (64%) · uncovered: 392</div>
          </div>
          <div className="metric">
            <div className="metric-value" style={{ color: "var(--green)" }}>{completed}</div>
            <div className="metric-label">Migrated</div>
            <div className="metric-bar"><div className="metric-bar-fill" style={{ width: `${(completed / 707) * 100}%`, background: "var(--green)" }} /></div>
          </div>
          <div className="metric">
            <div className="metric-value" style={{ color: "var(--accent)" }}>{running}</div>
            <div className="metric-label">Running</div>
          </div>
          <div className="metric">
            <div className="metric-value" style={{ color: "var(--amber)" }}>{review}</div>
            <div className="metric-label">Awaiting Review</div>
          </div>
          <div className="metric">
            <div className="metric-value">${totalCost.toFixed(2)}</div>
            <div className="metric-label">Total Spend</div>
            <div className="metric-bar"><div className="metric-bar-fill" style={{ width: `${(totalCost / 20000) * 100}%`, background: "var(--accent)" }} /></div>
            <div className="metric-sub">of $20,000 budget</div>
          </div>
        </div>

        {/* Active Pipelines */}
        <div className="table-wrap">
          <div className="table-toolbar">
            <h3>Active Pipelines</h3>
            <span className="spacer" />
            <div className="filter-group">
              <button className="filter-btn active">All</button>
              <button className="filter-btn">Running</button>
              <button className="filter-btn">Review</button>
              <button className="filter-btn">Failed</button>
            </div>
          </div>
          <table>
            <thead>
              <tr>
                <th>Page</th>
                <th>Module</th>
                <th>Complexity</th>
                <th>Status</th>
                <th>Step</th>
                <th>Cost</th>
              </tr>
            </thead>
            <tbody>
              {pages.map((p) => (
                <tr key={p.id}>
                  <td className="td-mono"><strong>{p.id}</strong></td>
                  <td className="td-mono">{p.module}</td>
                  <td><span className={`complexity complexity-${p.complexity || "med"}`}>{(p.complexity || "MED").toUpperCase()}</span></td>
                  <td><span className={`status status-${p.migration_status}`}>{p.migration_status}</span></td>
                  <td>{p.current_step}/9</td>
                  <td>${(p.total_cost || 0).toFixed(3)}</td>
                </tr>
              ))}
              {pages.length === 0 && (
                <tr><td colSpan={6} style={{ color: "var(--text3)", textAlign: "center", padding: 24 }}>No pages loaded. Start the orchestrator first.</td></tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Live Events */}
        {events.length > 0 && (
          <div style={{ marginTop: 16, background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: 14 }}>
            <h3 style={{ fontSize: 12, marginBottom: 8 }}>Live Events</h3>
            <div style={{ maxHeight: 200, overflowY: "auto" }}>
              {events.map((ev, i) => (
                <div key={i} style={{ padding: "4px 8px", marginBottom: 3, fontSize: 10, background: "var(--surface2)", borderRadius: 4, fontFamily: "var(--mono)" }}>
                  <span style={{ color: "var(--accent)" }}>{ev.event}</span>{" "}
                  <span style={{ color: "var(--text3)" }}>{JSON.stringify(ev.data)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
