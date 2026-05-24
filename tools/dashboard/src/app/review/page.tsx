"use client";

export default function ReviewQueue() {
  const reviews = [
    { id: 1, page: "shop_admin.af_member_analysis", step: "React Generation", type: "blocking", summary: "React 6 컴포넌트 생성 완료. Visual diff 3.4%. 확인 후 승인 또는 수정." },
    { id: 2, page: "shop_admin.item_list", step: "Spec + API Contract", type: "blocking", summary: "API Contract 13 endpoints 생성. Spec 일치 여부 확인 필요." },
    { id: 3, page: "sms_admin.sms_write", step: "Java Test — Tier 3", type: "failed", summary: "3회 자동 수정 실패. SMS 발송 API 타입 불일치. 수동 개입 필요." },
    { id: 4, page: "bbs.write", step: "Java Code", type: "info", summary: "Spring Boot Controller + Service 4파일. 테스트 전부 통과." },
    { id: 5, page: "core.member_list", step: "Spec Verify", type: "info", summary: "php_detect_gaps: 2건 unresolved_calls. dynamic include 경로 확인 필요." },
  ];

  return (
    <>
      <div className="header">
        <span style={{ fontSize: 12, color: "var(--text3)" }}>sk-main-php/adm / Review Queue</span>
      </div>
      <div className="content">
        <div style={{ display: "flex", gap: 0, borderBottom: "1px solid var(--border)", marginBottom: 16 }}>
          <div className="pane-tab active">Pending ({reviews.length})</div>
          <div className="pane-tab">Auto-fixed (12)</div>
          <div className="pane-tab">History</div>
        </div>

        {reviews.map((r) => (
          <div className="review-card" key={r.id}>
            <div className="review-card-head">
              <span className={`status status-${r.type === "failed" ? "failed" : "review"}`} />
              <span className="name">{r.page}</span>
              <span className="step">{r.step}</span>
              {r.type === "blocking" && <span className="tag tag-blocking">BLOCKING</span>}
              {r.type === "failed" && <span className="tag tag-failed">ESCALATED</span>}
            </div>
            <div className="review-card-body">{r.summary}</div>
          </div>
        ))}
      </div>
    </>
  );
}
