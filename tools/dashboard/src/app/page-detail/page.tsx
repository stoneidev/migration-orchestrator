"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useWebSocket } from "@/hooks/useWebSocket";

export default function PageDetailWrapper() {
  return (
    <Suspense fallback={<div className="content" style={{ padding: 40, color: "var(--text3)" }}>Loading...</div>}>
      <PageDetailPage />
    </Suspense>
  );
}

const STEP_NAMES: Record<number, string> = {
  1: "Spec Load",
  2: "Spec Verify",
  3: "API Contract",
  4: "React Generation",
  5: "Java Development",
  6: "Java Test",
  7: "Integration Test",
  8: "Equivalence Check",
  9: "Complete",
};

interface StepData {
  step_number: number;
  step_name: string;
  status: string;
  executions: Array<{
    attempt: number;
    status: string;
    model: string | null;
    cost: number | null;
    duration_ms: number | null;
    error: string | null;
    started_at: string | null;
  }>;
  artifacts: Array<{
    type: string;
    path: string;
    version: number;
  }>;
}

interface PageDetail {
  page_id: string;
  migration_status: string;
  current_step: number;
  total_cost: number;
  steps: StepData[];
}

function PageDetailPage() {
  const searchParams = useSearchParams();
  const pageId = searchParams.get("id") || "bbs.alert_close";
  const [detail, setDetail] = useState<PageDetail | null>(null);
  const [running, setRunning] = useState(false);
  const [services, setServices] = useState<any>(null);
  const { events } = useWebSocket();

  async function fetchServices() {
    try {
      const res = await fetch("http://localhost:8000/api/services/status");
      const data = await res.json();
      if (data.success) setServices(data.data);
    } catch {}
  }

  async function toggleService(name: string) {
    const svc = services?.[name];
    const action = svc?.status === "running" ? "stop" : "start";
    await fetch(`http://localhost:8000/api/services/${name}/${action}`, { method: "POST" });
    setTimeout(fetchServices, 2000);
  }

  async function fetchDetail() {
    try {
      const res = await fetch(`http://localhost:8000/api/pipeline/${pageId}/steps`);
      const data = await res.json();
      if (data.success) setDetail(data.data);
    } catch {}
  }

  useEffect(() => {
    fetchDetail();
    fetchServices();
  }, [pageId]);

  useEffect(() => {
    const relevant = events.filter((e) => e.data?.page_id === pageId);
    if (relevant.length > 0) {
      fetchDetail();
      setRunning(false);
    }
  }, [events]);

  async function runNextStep() {
    setRunning(true);
    try {
      await fetch("http://localhost:8000/api/pipeline/run-step", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ page_id: pageId }),
      });
    } catch {}
  }

  async function retryStep(stepNumber: number) {
    setRunning(true);
    try {
      await fetch("http://localhost:8000/api/pipeline/retry-step", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ page_id: pageId, step_number: stepNumber }),
      });
    } catch {}
  }

  async function runAll() {
    setRunning(true);
    try {
      await fetch("http://localhost:8000/api/pipeline/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ page_ids: [pageId] }),
      });
    } catch {}
  }

  const nextStep = detail ? detail.current_step + 1 : 1;
  const isComplete = detail?.migration_status === "complete";

  return (
    <>
      <div className="header">
        <span style={{ fontSize: 12, color: "var(--text3)" }}>
          Pages / {pageId} / Step-by-Step Execution
        </span>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          <button className="btn" onClick={runNextStep} disabled={running || isComplete}>
            {running ? "Running..." : isComplete ? "Complete" : `Run Step ${nextStep}`}
          </button>
          <button className="btn btn-primary" onClick={runAll} disabled={running || isComplete}>
            Run All Remaining
          </button>
        </div>
      </div>
      <div className="content">
        {/* Pipeline Strip */}
        <div className="pipeline-strip">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((n) => {
            const step = detail?.steps.find((s) => s.step_number === n);
            let cls = "pl-step pl-step-wait";
            if (step?.status === "passed") cls = "pl-step pl-step-done";
            else if (step?.status === "running") cls = "pl-step pl-step-active";
            else if (step?.status === "blocked") cls = "pl-step" + " " + "pl-step-wait";

            return (
              <span key={n}>
                <span className={cls}>
                  {step?.status === "passed" ? "✓" : n} {STEP_NAMES[n]}
                </span>
                {n < 9 && <span className="pl-conn" />}
              </span>
            );
          })}
        </div>

        {/* Info bar */}
        <div className="info-bar">
          <div className="info-item"><span className="k">Status:</span><span className="v">{detail?.migration_status || "—"}</span></div>
          <div className="info-item"><span className="k">Current Step:</span><span className="v">{detail?.current_step || 0}/9</span></div>
          <div className="info-item"><span className="k">Total Cost:</span><span className="v">${(detail?.total_cost || 0).toFixed(4)}</span></div>
        </div>

        {/* Services Launch */}
        {detail?.migration_status === "complete" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
            <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: 14 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                <span style={{ fontSize: 12, fontWeight: 600 }}>Frontend (React)</span>
                <span className={`status status-${services?.frontend?.status === "running" ? "running" : "queued"}`} style={{ marginLeft: "auto" }}>
                  {services?.frontend?.status || "stopped"}
                </span>
              </div>
              <div style={{ fontSize: 10, color: "var(--text3)", marginBottom: 8 }}>
                {services?.frontend?.status === "running"
                  ? <a href={services.frontend.url + "/admin/" + pageId.replace(".", "/")} target="_blank" style={{ color: "var(--accent)" }}>{services.frontend.url}/admin/{pageId.replace(".", "/")}</a>
                  : "Next.js dev server on port 3001"}
              </div>
              <button className={services?.frontend?.status === "running" ? "btn" : "btn btn-primary"} onClick={() => toggleService("frontend")} style={{ width: "100%", fontSize: 11 }}>
                {services?.frontend?.status === "running" ? "Stop Frontend" : "Launch Frontend"}
              </button>
            </div>
            <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: 14 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                <span style={{ fontSize: 12, fontWeight: 600 }}>Backend (Java)</span>
                <span className={`status status-${services?.backend?.status === "running" ? "running" : "queued"}`} style={{ marginLeft: "auto" }}>
                  {services?.backend?.status || "stopped"}
                </span>
              </div>
              <div style={{ fontSize: 10, color: "var(--text3)", marginBottom: 8 }}>
                {services?.backend?.status === "running"
                  ? <a href={services.backend.url} target="_blank" style={{ color: "var(--accent)" }}>{services.backend.url}</a>
                  : "Spring Boot on port 8080"}
              </div>
              <button className={services?.backend?.status === "running" ? "btn" : "btn btn-primary"} onClick={() => toggleService("backend")} style={{ width: "100%", fontSize: 11 }}>
                {services?.backend?.status === "running" ? "Stop Backend" : "Launch Backend"}
              </button>
            </div>
          </div>
        )}

        {/* Step details */}
        <div className="table-wrap">
          <div className="table-toolbar">
            <h3>Step Execution History</h3>
          </div>
          <table>
            <thead>
              <tr>
                <th>Step</th>
                <th>Name</th>
                <th>Status</th>
                <th>Model</th>
                <th>Cost</th>
                <th>Duration</th>
                <th>Artifacts</th>
                <th>Error</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {detail?.steps.map((step) => (
                <tr key={step.step_number}>
                  <td>{step.step_number}</td>
                  <td className="td-mono">{step.step_name}</td>
                  <td>
                    <span className={`status status-${step.status === "passed" ? "complete" : step.status === "pending" ? "queued" : step.status}`}>
                      {step.status}
                    </span>
                  </td>
                  <td className="td-mono">{step.executions.at(-1)?.model || "—"}</td>
                  <td>${(step.executions.at(-1)?.cost || 0).toFixed(4)}</td>
                  <td>{step.executions.at(-1)?.duration_ms ? `${step.executions.at(-1)!.duration_ms}ms` : "—"}</td>
                  <td>{step.artifacts.length > 0 ? step.artifacts.map((a) => a.type).join(", ") : "—"}</td>
                  <td style={{ maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", color: "var(--red)" }}>
                    {step.executions.at(-1)?.error || ""}
                  </td>
                  <td>
                    <button
                      className="btn"
                      style={{ fontSize: 9, padding: "2px 6px" }}
                      onClick={() => retryStep(step.step_number)}
                      disabled={running}
                    >
                      Retry
                    </button>
                  </td>
                </tr>
              ))}
              {(!detail || detail.steps.length === 0) && (
                <tr>
                  <td colSpan={8} style={{ textAlign: "center", color: "var(--text3)", padding: 24 }}>
                    No steps executed yet. Click "Run Step 1" to start.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Live Events for this page */}
        {events.filter((e) => e.data?.page_id === pageId).length > 0 && (
          <div style={{ marginTop: 16, background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: 14 }}>
            <h3 style={{ fontSize: 12, marginBottom: 8 }}>Live Events</h3>
            <div style={{ maxHeight: 150, overflowY: "auto" }}>
              {events
                .filter((e) => e.data?.page_id === pageId)
                .map((ev, i) => (
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
