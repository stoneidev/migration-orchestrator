"use client";

export default function CostPage() {
  return (
    <>
      <div className="header">
        <span style={{ fontSize: 12, color: "var(--text3)" }}>sk-main-php/adm / Cost Analysis</span>
      </div>
      <div className="content">
        <div className="grid grid-4" style={{ marginBottom: 20 }}>
          <div className="metric">
            <div className="metric-label">Total Spend</div>
            <div className="metric-value">$18.42</div>
            <div className="metric-bar"><div className="metric-bar-fill" style={{ width: "0.09%", background: "var(--accent)" }} /></div>
            <div className="metric-sub">of $20,000 budget</div>
          </div>
          <div className="metric">
            <div className="metric-label">Avg / Page</div>
            <div className="metric-value">$0.38</div>
            <div className="metric-sub" style={{ color: "var(--green)" }}>↓12% vs pages 1–10</div>
          </div>
          <div className="metric">
            <div className="metric-label">Cache Hit</div>
            <div className="metric-value" style={{ color: "var(--green)" }}>64%</div>
            <div className="metric-sub">saving $11.20</div>
          </div>
          <div className="metric">
            <div className="metric-label">Auto-fix Rate</div>
            <div className="metric-value">82%</div>
            <div className="metric-sub" style={{ color: "var(--green)" }}>↑22% from initial</div>
          </div>
        </div>

        <div className="grid grid-2">
          <div className="table-wrap">
            <div className="table-toolbar"><h3>By Model</h3></div>
            <table>
              <thead><tr><th>Model</th><th>Calls</th><th>Input</th><th>Output</th><th>Cost</th><th>Share</th></tr></thead>
              <tbody>
                <tr><td><strong>Opus 4</strong></td><td>96</td><td>412K</td><td>89K</td><td>$11.23</td><td>61%</td></tr>
                <tr><td><strong>Sonnet 4</strong></td><td>384</td><td>1.2M</td><td>420K</td><td>$5.89</td><td>32%</td></tr>
                <tr><td><strong>Haiku 4</strong></td><td>612</td><td>2.1M</td><td>380K</td><td>$1.30</td><td>7%</td></tr>
              </tbody>
            </table>
          </div>
          <div className="table-wrap">
            <div className="table-toolbar"><h3>By Step</h3></div>
            <table>
              <thead><tr><th>Step</th><th>Avg Tokens</th><th>Avg Cost</th><th>1st-try Pass</th></tr></thead>
              <tbody>
                <tr><td>Spec Verify</td><td>4,200</td><td>$0.02</td><td>94%</td></tr>
                <tr><td>API Contract</td><td>5,100</td><td>$0.04</td><td>89%</td></tr>
                <tr><td>React Gen</td><td>18,400</td><td>$0.12</td><td>72%</td></tr>
                <tr><td>Java Dev</td><td>22,600</td><td>$0.15</td><td>68%</td></tr>
                <tr><td>Java Test</td><td>8,200</td><td>$0.03</td><td>78%</td></tr>
                <tr><td>Integration</td><td>12,100</td><td>$0.05</td><td>82%</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
}
