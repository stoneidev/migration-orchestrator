const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchPages() {
  const res = await fetch(`${API_BASE}/api/pages`);
  const data = await res.json();
  return data.data || [];
}

export async function fetchPageDetail(pageId: string) {
  const res = await fetch(`${API_BASE}/api/pages/${pageId}`);
  const data = await res.json();
  return data.data;
}

export async function runPipeline(pageIds: string[]) {
  const res = await fetch(`${API_BASE}/api/pipeline/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ page_ids: pageIds }),
  });
  return res.json();
}

export async function getPipelineStatus() {
  const res = await fetch(`${API_BASE}/api/pipeline/status`);
  const data = await res.json();
  return data.data || {};
}
