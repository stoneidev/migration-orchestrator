"use client";

import { useEffect, useState } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";

const API = "http://localhost:8000";

export default function NewPageSpec() {
  const [url, setUrl] = useState("https://www.stylekorean.com/myambassador?device=mobile");
  const [phpPath, setPhpPath] = useState("mobile/shop/ambassador/my_page.php");
  const [pageId, setPageId] = useState("ambassador.my_page");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [session, setSession] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<any[]>([]);
  const { events } = useWebSocket();

  useEffect(() => {
    fetch(`${API}/api/spec-gen/history`).then(r => r.json()).then(d => setHistory(d.data || [])).catch(() => {});
  }, [session?.status]);

  async function fetchSession(sid: string) {
    const res = await fetch(`${API}/api/spec-gen/${sid}`);
    const data = await res.json();
    if (data.success) setSession(data.data);
  }

  async function startSession() {
    const res = await fetch(`${API}/api/spec-gen/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, php_path: phpPath, page_id: pageId }),
    });
    const data = await res.json();
    if (data.success) {
      setSessionId(data.data.session_id);
      setSession(data.data);
    }
  }

  async function runStep(step: number) {
    if (!sessionId) return;
    setLoading(true);
    const endpoint = step === 1 ? "step1-capture" : step === 2 ? "step2-analyze" : "step3-generate";
    await fetch(`${API}/api/spec-gen/${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId }),
    });
    // Poll for completion
    const poll = setInterval(async () => {
      await fetchSession(sessionId);
      const s = (await (await fetch(`${API}/api/spec-gen/${sessionId}`)).json()).data;
      setSession(s);
      if (s.status !== "capturing" && s.status !== "analyzing" && s.status !== "generating") {
        setLoading(false);
        clearInterval(poll);
      }
    }, 2000);
  }

  const stepStatus = (step: number) => {
    if (!session) return "pending";
    // Step completion is determined by session status progression
    const statusMap: Record<string, number> = {
      "ready": 0,
      "capturing": 1,
      "captured": 1,
      "analyzing": 2,
      "analyzed": 2,
      "generating": 3,
      "complete": 3,
    };
    const completedStep = statusMap[session.status] || 0;
    const isStepDone = (step === 1 && ["captured", "analyzed", "analyzing", "generating", "complete"].includes(session.status)) ||
                       (step === 2 && ["analyzed", "generating", "complete"].includes(session.status)) ||
                       (step === 3 && session.status === "complete");

    if (isStepDone) return "done";
    if (session.step === step && loading) return "running";
    if (session.status === "error" && session.step === step) return "error";
    return "pending";
  };

  return (
    <>
      <div className="header">
        <span style={{ fontSize: 12, color: "var(--text3)" }}>Workspace / New Page — Spec Generation</span>
      </div>
      <div className="content">
        {/* Input */}
        <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: 16, marginBottom: 16 }}>
          <h3 style={{ fontSize: 13, marginBottom: 12 }}>New Page Configuration</h3>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, marginBottom: 12 }}>
            <div>
              <label style={{ fontSize: 11, color: "var(--text3)", display: "block", marginBottom: 4 }}>Page URL</label>
              <input value={url} onChange={(e) => setUrl(e.target.value)} style={{ width: "100%", padding: "7px 10px", background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 6, color: "var(--text)", fontSize: 11 }} />
            </div>
            <div>
              <label style={{ fontSize: 11, color: "var(--text3)", display: "block", marginBottom: 4 }}>PHP File Path</label>
              <input value={phpPath} onChange={(e) => setPhpPath(e.target.value)} style={{ width: "100%", padding: "7px 10px", background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 6, color: "var(--text)", fontSize: 11 }} />
            </div>
            <div>
              <label style={{ fontSize: 11, color: "var(--text3)", display: "block", marginBottom: 4 }}>Page ID</label>
              <input value={pageId} onChange={(e) => setPageId(e.target.value)} style={{ width: "100%", padding: "7px 10px", background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 6, color: "var(--text)", fontSize: 11 }} />
            </div>
          </div>
          <button className="btn btn-primary" onClick={startSession} disabled={!!sessionId}>
            {sessionId ? `Session: ${sessionId}` : "Create Session"}
          </button>
        </div>

        {/* Pipeline Steps */}
        {sessionId && (
          <>
            <div className="pipeline-strip">
              <span className={`pl-step ${stepStatus(1) === "done" ? "pl-step-done" : stepStatus(1) === "running" ? "pl-step-active" : "pl-step-wait"}`}>
                {stepStatus(1) === "done" ? "✓" : "1"} Playwright Capture
              </span>
              <span className="pl-conn" />
              <span className={`pl-step ${stepStatus(2) === "done" ? "pl-step-done" : stepStatus(2) === "running" ? "pl-step-active" : "pl-step-wait"}`}>
                {stepStatus(2) === "done" ? "✓" : "2"} MCP Analysis
              </span>
              <span className="pl-conn" />
              <span className={`pl-step ${stepStatus(3) === "done" ? "pl-step-done" : stepStatus(3) === "running" ? "pl-step-active" : "pl-step-wait"}`}>
                {stepStatus(3) === "done" ? "✓" : "3"} Spec Generation
              </span>
            </div>

            {/* Step 1: Capture */}
            <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: 16, marginBottom: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                <h4 style={{ fontSize: 12, fontWeight: 600 }}>Step 1: Playwright Capture</h4>
                <button className="btn" onClick={() => runStep(1)} disabled={loading || stepStatus(1) === "done"} style={{ marginLeft: "auto" }}>
                  {loading && session?.step === 1 ? "Capturing..." : stepStatus(1) === "done" ? "✓ Done" : "Run"}
                </button>
              </div>
              {session?.screenshot && (
                <div style={{ fontSize: 11, color: "var(--text2)" }}>
                  <div>URL: <code>{session.screenshot.url}</code></div>
                  <div>Title: {session.screenshot.title}</div>
                  <div>Headings: {session.screenshot.headings?.join(", ")}</div>
                  <div>Buttons: {session.screenshot.buttons?.join(", ")}</div>
                </div>
              )}
            </div>

            {/* Step 2: MCP Analysis */}
            <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: 16, marginBottom: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                <h4 style={{ fontSize: 12, fontWeight: 600 }}>Step 2: MCP PHP Analysis</h4>
                <button className="btn" onClick={() => runStep(2)} disabled={loading || stepStatus(1) !== "done" || stepStatus(2) === "done"} style={{ marginLeft: "auto" }}>
                  {loading && session?.step === 2 ? "Analyzing..." : stepStatus(2) === "done" ? "✓ Done" : "Run"}
                </button>
              </div>
              {session?.mcp_data && (
                <div style={{ fontSize: 11, color: "var(--text2)" }}>
                  <div>Includes: {session.mcp_data.file_detail?.includes?.length || 0}</div>
                  <div>SQL Queries: {session.mcp_data.trace?.sql_count || 0}</div>
                  <div>Execution Steps: {session.mcp_data.trace?.step_count || 0}</div>
                  <div>Functions: {session.mcp_data.file_detail?.calls?.map((c: any) => c.name).join(", ")}</div>
                </div>
              )}
            </div>

            {/* Step 3: Spec Generation */}
            <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: 16, marginBottom: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                <h4 style={{ fontSize: 12, fontWeight: 600 }}>Step 3: AI Spec Generation (Bedrock Sonnet)</h4>
                <button className="btn btn-primary" onClick={() => runStep(3)} disabled={loading || stepStatus(2) !== "done" || stepStatus(3) === "done"} style={{ marginLeft: "auto" }}>
                  {loading && session?.step === 3 ? "Generating..." : stepStatus(3) === "done" ? "✓ Done" : "Generate Spec"}
                </button>
              </div>
              {session?.spec && (
                <div style={{ fontSize: 11 }}>
                  <div style={{ color: "var(--green)", marginBottom: 8 }}>
                    ✓ Generated: {session.spec.operations?.length || 0} Operations, {session.spec.business_rules?.length || 0} Business Rules, {session.spec.test_scenarios?.length || 0} Test Scenarios
                  </div>
                  <details>
                    <summary style={{ cursor: "pointer", color: "var(--accent)", fontSize: 11 }}>View Generated Spec</summary>
                    <pre style={{ background: "var(--bg)", border: "1px solid var(--border)", borderRadius: 6, padding: 12, marginTop: 8, fontSize: 10, maxHeight: 400, overflow: "auto", color: "var(--text2)" }}>
                      {JSON.stringify(session.spec, null, 2)}
                    </pre>
                  </details>
                </div>
              )}
            </div>

            {/* Error display */}
            {session?.error && (
              <div style={{ background: "var(--red-muted)", border: "1px solid var(--red)", borderRadius: 8, padding: 12, fontSize: 11, color: "var(--red)" }}>
                Error: {session.error}
              </div>
            )}

            {/* Next: Pipeline */}
            {session?.status === "complete" && (
              <div style={{ marginTop: 16, padding: 16, background: "var(--green-muted)", border: "1px solid var(--green)", borderRadius: 8 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: "var(--green)", marginBottom: 8 }}>✓ Spec Generation Complete</div>
                <div style={{ fontSize: 11, color: "var(--text2)", marginBottom: 12 }}>
                  이제 이 Spec으로 마이그레이션 파이프라인을 실행할 수 있습니다.
                </div>
                <a href={`/page-detail?id=${pageId}`} className="btn btn-primary">
                  Start Migration Pipeline →
                </a>
              </div>
            )}
          </>
        )}

        {/* History */}
        {history.length > 0 && (
          <div className="table-wrap" style={{ marginTop: 20 }}>
            <div className="table-toolbar">
              <h3>Generation History</h3>
            </div>
            <table>
              <thead>
                <tr><th>Page ID</th><th>URL</th><th>PHP Path</th><th>Status</th><th>Ops</th><th>BRs</th><th>TSs</th><th>Cost</th><th>Created</th></tr>
              </thead>
              <tbody>
                {history.map((h: any, i: number) => (
                  <tr key={i}>
                    <td className="td-mono">{h.page_id}</td>
                    <td style={{ maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis" }}>{h.url}</td>
                    <td className="td-mono" style={{ fontSize: 10 }}>{h.php_path}</td>
                    <td><span className={`status status-${h.status === "complete" ? "complete" : "failed"}`}>{h.status}</span></td>
                    <td>{h.operations}</td>
                    <td>{h.business_rules}</td>
                    <td>{h.test_scenarios}</td>
                    <td>${(h.cost || 0).toFixed(4)}</td>
                    <td style={{ fontSize: 10 }}>{h.created_at?.slice(0, 19)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Live Events */}
        {events.filter((e) => e.event.startsWith("spec_gen:")).length > 0 && (
          <div style={{ marginTop: 16, background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, padding: 14 }}>
            <h3 style={{ fontSize: 12, marginBottom: 8 }}>Events</h3>
            <div style={{ maxHeight: 150, overflowY: "auto" }}>
              {events.filter((e) => e.event.startsWith("spec_gen:")).map((ev, i) => (
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
