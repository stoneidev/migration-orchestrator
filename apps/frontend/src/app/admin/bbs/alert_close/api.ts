/**
 * Alert Close API Client
 * Backend: http://localhost:8080/api/v1/admin/bbs/alert-close
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api';
const ALERT_CLOSE_ENDPOINT = `${API_BASE_URL}/v1/admin/bbs/alert-close`;

export interface AlertCloseResponse {
  html: string;
}

/**
 * Render alert close popup from backend
 * Falls back to client-side rendering if backend is unavailable
 */
export async function renderAlertClose(params: {
  msg?: string;
  error?: string;
}): Promise<{ success: boolean; html?: string; error?: string }> {
  try {
    const queryParams = new URLSearchParams();
    if (params.msg) queryParams.set('msg', params.msg);
    if (params.error) queryParams.set('error', params.error);

    const url = `${ALERT_CLOSE_ENDPOINT}?${queryParams.toString()}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'text/html',
      },
      signal: AbortSignal.timeout(3000),
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    const html = await response.text();
    return { success: true, html };
  } catch (error) {
    console.warn('Backend API unavailable, using client-side rendering:', error);
    return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
  }
}

/**
 * Check if backend is available
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/v1/admin/bbs/alert-close`, {
      method: 'GET',
      signal: AbortSignal.timeout(1000),
    });
    return response.ok;
  } catch {
    return false;
  }
}
