"use client";

import { useEffect, useState } from "react";
import { fetchPages } from "@/lib/api";

export default function PagesPage() {
  const [pages, setPages] = useState<any[]>([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    fetchPages().then(setPages).catch(() => {});
  }, []);

  const filtered = filter === "all" ? pages : pages.filter((p) => p.migration_status === filter);

  return (
    <>
      <div className="header">
        <span style={{ fontSize: 12, color: "var(--text3)" }}>sk-main-php/adm / All Specs (707)</span>
        <div style={{ marginLeft: "auto" }}>
          <input
            type="text"
            placeholder="Search..."
            style={{ background: "var(--bg)", border: "1px solid var(--border)", borderRadius: "var(--radius)", padding: "4px 8px", fontSize: 11, color: "var(--text)", width: 180, outline: "none" }}
          />
        </div>
      </div>
      <div className="content">
        <div className="table-wrap">
          <div className="table-toolbar">
            <h3>All Specs ({filtered.length})</h3>
            <span className="spacer" />
            <div className="filter-group">
              {["all", "complete", "running", "queued", "failed"].map((f) => (
                <button key={f} className={`filter-btn ${filter === f ? "active" : ""}`} onClick={() => setFilter(f)}>
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>
          </div>
          <table>
            <thead>
              <tr><th>Spec ID</th><th>Title</th><th>Module</th><th>Status</th><th>Step</th><th>Cost</th></tr>
            </thead>
            <tbody>
              {filtered.map((p: any) => (
                <tr key={p.id} onClick={() => window.location.href = `/page-detail?id=${p.id}`} style={{ cursor: "pointer" }}>
                  <td className="td-mono">{p.id}</td>
                  <td>{p.title || "—"}</td>
                  <td className="td-mono">{p.module}</td>
                  <td><span className={`status status-${p.migration_status}`}>{p.migration_status}</span></td>
                  <td>{p.current_step}/9</td>
                  <td>${(p.total_cost || 0).toFixed(3)}</td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={6} style={{ color: "var(--text3)", textAlign: "center", padding: 24 }}>No pages. Start orchestrator with `uvicorn src.main:app`</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
