"use client";

export default function PatternsPage() {
  const patterns = [
    { id: "PAT-001", php: "sql_fetch(\"SELECT...\")", target: "{Table}Repository.findBy{Condition}()", confidence: 98, pages: 42 },
    { id: "PAT-002", php: "$_SESSION['ss_mb_id']", target: "SecurityContextHolder.getContext().getAuthentication()", confidence: 95, pages: 38 },
    { id: "PAT-003", php: "sql_query(\"INSERT...\")", target: "{table}Repository.save(entity)", confidence: 97, pages: 31 },
    { id: "PAT-004", php: "auth_check($member,'admin')", target: "@PreAuthorize(\"hasRole('ADMIN')\")", confidence: 96, pages: 45 },
    { id: "PAT-005", php: "get_paging(...)", target: "PageRequest.of(page, size)", confidence: 94, pages: 28 },
  ];

  const prefs = [
    { id: "PREF-001", rule: "테이블 컴포넌트: 항상 sticky header 적용", source: "cs_list refinement", applies: "list pages" },
    { id: "PREF-002", rule: "날짜 필터: date-range picker 사용", source: "order_list refinement", applies: "date filter pages" },
    { id: "PREF-003", rule: "Form: React Hook Form + Zod validation", source: "item_edit refinement", applies: "form pages" },
  ];

  return (
    <>
      <div className="header">
        <span style={{ fontSize: 12, color: "var(--text3)" }}>Intelligence / Pattern Library (142)</span>
      </div>
      <div className="content">
        <div style={{ display: "flex", gap: 0, borderBottom: "1px solid var(--border)", marginBottom: 16 }}>
          <div className="pane-tab active">PHP→Java (58)</div>
          <div className="pane-tab">PHP→React (34)</div>
          <div className="pane-tab">Preferences (12)</div>
          <div className="pane-tab">Entities (38)</div>
        </div>

        <div className="spec-group">
          <div className="spec-group-title">Learned PHP→Java Patterns</div>
          {patterns.map((p) => (
            <div className="spec-card" key={p.id}>
              <div className="id">{p.id}</div>
              <div className="desc">
                <code style={{ background: "var(--surface2)", padding: "1px 4px", borderRadius: 3, fontSize: 10, color: "var(--cyan)" }}>{p.php}</code>
                {" → "}
                <code style={{ background: "var(--surface2)", padding: "1px 4px", borderRadius: 3, fontSize: 10, color: "var(--green)" }}>{p.target}</code>
              </div>
              <div className="meta">Confidence {p.confidence}% · {p.pages} pages</div>
            </div>
          ))}
        </div>

        <div className="spec-group" style={{ marginTop: 24 }}>
          <div className="spec-group-title">User Preferences</div>
          {prefs.map((p) => (
            <div className="spec-card" key={p.id}>
              <div className="id">{p.id}</div>
              <div className="desc">{p.rule}</div>
              <div className="meta">Source: {p.source} · Applies to: {p.applies}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
