"use client";

import { useEffect, useState } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";

interface ProjectStatus {
  frontend: { initialized: boolean; status: string };
  backend: { initialized: boolean; status: string };
}

export default function SettingsPage() {
  const [projectStatus, setProjectStatus] = useState<ProjectStatus | null>(null);
  const [initializing, setInitializing] = useState(false);
  const { events } = useWebSocket();

  useEffect(() => {
    fetchStatus();
  }, []);

  // Listen for init events
  useEffect(() => {
    const initEvents = events.filter((e) => e.event.startsWith("project:"));
    if (initEvents.length > 0) {
      fetchStatus();
    }
  }, [events]);

  async function fetchStatus() {
    try {
      const res = await fetch("http://localhost:8000/api/project/status");
      const data = await res.json();
      setProjectStatus(data.data);
    } catch {}
  }

  async function initProject(targets: string[]) {
    setInitializing(true);
    try {
      await fetch("http://localhost:8000/api/project/init", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ targets }),
      });
    } catch {}
  }

  return (
    <>
      <div className="header">
        <span style={{ fontSize: 12, color: "var(--text3)" }}>System / Settings</span>
      </div>
      <div className="content">
        {/* Project Initialization */}
        <div style={{ marginBottom: 32 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>Project Initialization</h2>
          <p style={{ fontSize: 12, color: "var(--text2)", marginBottom: 16 }}>
            마이그레이션 대상 프로젝트(Frontend + Backend)의 초기 scaffold를 생성합니다.
            Claude CLI가 프로젝트 구조, 설정 파일, 공통 모듈을 자동 생성합니다.
          </p>

          <div className="grid grid-2" style={{ maxWidth: 700 }}>
            {/* Frontend */}
            <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: 16 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <span style={{ fontSize: 13, fontWeight: 600 }}>Frontend</span>
                {projectStatus?.frontend.initialized ? (
                  <span className="status status-complete">Initialized</span>
                ) : projectStatus?.frontend.status === "running" ? (
                  <span className="status status-running">Initializing...</span>
                ) : (
                  <span className="status status-queued">Not initialized</span>
                )}
              </div>
              <div style={{ fontSize: 11, color: "var(--text3)", marginBottom: 12 }}>
                Next.js 15 + TypeScript + FSD + shadcn/ui + TanStack Query + Zustand + Pretendard
              </div>
              <button
                className="btn btn-primary"
                onClick={() => initProject(["frontend"])}
                disabled={projectStatus?.frontend.status === "running"}
                style={{ width: "100%" }}
              >
                {projectStatus?.frontend.initialized ? "Re-initialize Frontend" : "Initialize Frontend"}
              </button>
            </div>

            {/* Backend */}
            <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: 16 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <span style={{ fontSize: 13, fontWeight: 600 }}>Backend</span>
                {projectStatus?.backend.initialized ? (
                  <span className="status status-complete">Initialized</span>
                ) : projectStatus?.backend.status === "running" ? (
                  <span className="status status-running">Initializing...</span>
                ) : (
                  <span className="status status-queued">Not initialized</span>
                )}
              </div>
              <div style={{ fontSize: 11, color: "var(--text3)", marginBottom: 12 }}>
                Spring Boot 3.4 + Java 21 + Gradle + DDD/Hexagonal + Flyway + Lombok + MapStruct
              </div>
              <button
                className="btn btn-primary"
                onClick={() => initProject(["backend"])}
                disabled={projectStatus?.backend.status === "running"}
                style={{ width: "100%" }}
              >
                {projectStatus?.backend.initialized ? "Re-initialize Backend" : "Initialize Backend"}
              </button>
            </div>
          </div>

          {/* Initialize Both */}
          <div style={{ marginTop: 12 }}>
            <button
              className="btn"
              onClick={() => initProject(["frontend", "backend"])}
              disabled={initializing}
              style={{ marginRight: 8 }}
            >
              Initialize Both
            </button>
          </div>

          {/* Status details */}
          {projectStatus && (
            <div style={{ marginTop: 16, fontSize: 11, color: "var(--text3)" }}>
              <div>Frontend status: {projectStatus.frontend.status}</div>
              <div>Backend status: {projectStatus.backend.status}</div>
            </div>
          )}
        </div>

        {/* Init Events */}
        {events.filter((e) => e.event.startsWith("project:")).length > 0 && (
          <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: 14, marginBottom: 24 }}>
            <h3 style={{ fontSize: 12, marginBottom: 8 }}>Initialization Log</h3>
            <div style={{ maxHeight: 200, overflowY: "auto" }}>
              {events
                .filter((e) => e.event.startsWith("project:"))
                .map((ev, i) => (
                  <div key={i} style={{ padding: "4px 8px", marginBottom: 3, fontSize: 10, background: "var(--surface2)", borderRadius: 4, fontFamily: "var(--mono)" }}>
                    <span style={{ color: "var(--accent)" }}>{ev.event}</span>{" "}
                    <span style={{ color: "var(--text3)" }}>{JSON.stringify(ev.data)}</span>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Configuration */}
        <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 16 }}>Configuration</h2>
        <div style={{ maxWidth: 500 }}>
          <div style={{ marginBottom: 14 }}>
            <label style={{ display: "block", fontSize: 11, fontWeight: 500, color: "var(--text2)", marginBottom: 4 }}>Specs Directory</label>
            <input defaultValue="/Users/stoni/Projects/silicon2/harness/specs" style={{ width: "100%", padding: "7px 10px", background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 6, color: "var(--text)", fontSize: 12 }} readOnly />
          </div>
          <div style={{ marginBottom: 14 }}>
            <label style={{ display: "block", fontSize: 11, fontWeight: 500, color: "var(--text2)", marginBottom: 4 }}>PHP Project Root</label>
            <input defaultValue="/Users/stoni/Projects/silicon2/sk-main-php" style={{ width: "100%", padding: "7px 10px", background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 6, color: "var(--text)", fontSize: 12 }} readOnly />
          </div>
          <div style={{ marginBottom: 14 }}>
            <label style={{ display: "block", fontSize: 11, fontWeight: 500, color: "var(--text2)", marginBottom: 4 }}>MCP Server Path</label>
            <input defaultValue="/Users/stoni/.mcp-servers/php-analyzer" style={{ width: "100%", padding: "7px 10px", background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 6, color: "var(--text)", fontSize: 12 }} readOnly />
          </div>
          <div style={{ marginBottom: 14 }}>
            <label style={{ display: "block", fontSize: 11, fontWeight: 500, color: "var(--text2)", marginBottom: 4 }}>Max Parallel Pages</label>
            <input defaultValue="5" type="number" style={{ width: 80, padding: "7px 10px", background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 6, color: "var(--text)", fontSize: 12 }} readOnly />
          </div>
          <div style={{ marginBottom: 14 }}>
            <label style={{ display: "block", fontSize: 11, fontWeight: 500, color: "var(--text2)", marginBottom: 4 }}>Project Budget</label>
            <input defaultValue="$20,000" style={{ width: 120, padding: "7px 10px", background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 6, color: "var(--text)", fontSize: 12 }} readOnly />
          </div>
        </div>
      </div>
    </>
  );
}
