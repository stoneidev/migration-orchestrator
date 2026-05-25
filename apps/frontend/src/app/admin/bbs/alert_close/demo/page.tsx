'use client';

import { useState } from 'react';
import { renderAlertClose } from '../api';

/**
 * Demo page to test alert-close functionality
 * This page demonstrates both backend-rendered and client-side rendering modes
 */
export default function AlertCloseDemoPage() {
  const [message, setMessage] = useState('저장되었습니다.');
  const [isError, setIsError] = useState(false);
  const [useBackend, setUseBackend] = useState(true);
  const [apiStatus, setApiStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [lastResponse, setLastResponse] = useState<string>('');

  const handleTestAlert = async () => {
    if (useBackend) {
      // Test backend API
      setApiStatus('loading');
      const result = await renderAlertClose({
        msg: message,
        error: isError ? 'true' : 'false',
      });

      if (result.success && result.html) {
        setApiStatus('success');
        setLastResponse(result.html.substring(0, 500) + '...');
      } else {
        setApiStatus('error');
        setLastResponse(`Backend error: ${result.error}`);
      }
    } else {
      // Open client-side popup
      const params = new URLSearchParams({
        msg: message,
        error: isError ? 'true' : 'false',
      });
      window.open(
        `/admin/bbs/alert_close?${params.toString()}`,
        'alertPopup',
        'width=450,height=350,scrollbars=no,resizable=no'
      );
      setApiStatus('success');
      setLastResponse('Client-side popup opened');
    }
  };

  const handleOpenBackendPopup = () => {
    const params = new URLSearchParams({
      msg: message,
      error: isError ? 'true' : 'false',
    });
    const backendUrl = `http://localhost:8080/api/v1/admin/bbs/alert-close?${params.toString()}`;
    window.open(backendUrl, 'alertPopup', 'width=450,height=350,scrollbars=no,resizable=no');
    setApiStatus('success');
    setLastResponse('Backend popup opened directly');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Alert Close Demo
          </h1>
          <p className="text-gray-600 mb-8">
            관리자 경고/확인 팝업 후 창 닫기 API 테스트 페이지
          </p>

          {/* Configuration Panel */}
          <div className="space-y-6 mb-8">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                메시지
              </label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={3}
                placeholder="표시할 메시지를 입력하세요..."
              />
              <p className="mt-1 text-xs text-gray-500">
                줄바꿈은 \n 으로 입력 (예: "저장되었습니다.\n창이 닫힙니다.")
              </p>
            </div>

            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={isError}
                  onChange={(e) => setIsError(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">
                  오류 모드 (빨간색 스타일)
                </span>
              </label>
            </div>

            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={useBackend}
                  onChange={(e) => setUseBackend(e.target.checked)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">
                  백엔드 API 사용 (체크 해제 시 프론트엔드 렌더링)
                </span>
              </label>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 mb-8">
            <button
              onClick={handleTestAlert}
              className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 active:scale-95 transition-all shadow-md"
            >
              {useBackend ? 'API 테스트 (HTML 응답 확인)' : '팝업 열기 (클라이언트)'}
            </button>

            <button
              onClick={handleOpenBackendPopup}
              className="px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 active:scale-95 transition-all shadow-md"
            >
              백엔드 팝업 직접 열기
            </button>
          </div>

          {/* API Status */}
          {apiStatus !== 'idle' && (
            <div
              className={`p-4 rounded-lg mb-8 ${
                apiStatus === 'loading'
                  ? 'bg-blue-50 border border-blue-200'
                  : apiStatus === 'success'
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-red-50 border border-red-200'
              }`}
            >
              <h3 className="font-semibold text-sm mb-2">
                {apiStatus === 'loading' && '⏳ 로딩 중...'}
                {apiStatus === 'success' && '✅ 성공'}
                {apiStatus === 'error' && '❌ 오류'}
              </h3>
              {lastResponse && (
                <pre className="text-xs bg-white p-3 rounded border overflow-x-auto">
                  {lastResponse}
                </pre>
              )}
            </div>
          )}

          {/* Documentation */}
          <div className="border-t pt-8 mt-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              사용 방법
            </h2>

            <div className="space-y-4 text-sm">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-900 mb-2">
                  1. 백엔드 API 직접 호출
                </h3>
                <code className="block bg-white p-3 rounded border text-xs overflow-x-auto">
                  {`window.open('http://localhost:8080/api/v1/admin/bbs/alert-close?msg=저장되었습니다&error=false', ...)`}
                </code>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-900 mb-2">
                  2. 프론트엔드 페이지 사용
                </h3>
                <code className="block bg-white p-3 rounded border text-xs overflow-x-auto">
                  {`window.open('/admin/bbs/alert_close?msg=저장되었습니다&error=false', ...)`}
                </code>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-900 mb-2">
                  3. API 클라이언트 사용
                </h3>
                <code className="block bg-white p-3 rounded border text-xs overflow-x-auto">
                  {`import { renderAlertClose } from '@/app/admin/bbs/alert_close/api';
const result = await renderAlertClose({ msg: '저장되었습니다', error: 'false' });`}
                </code>
              </div>
            </div>
          </div>

          {/* API Spec */}
          <div className="border-t pt-8 mt-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              API 명세
            </h2>
            <div className="bg-gray-50 p-4 rounded-lg text-sm space-y-2">
              <div>
                <span className="font-semibold">Endpoint:</span>{' '}
                <code className="bg-white px-2 py-1 rounded text-xs">
                  GET /api/v1/admin/bbs/alert-close
                </code>
              </div>
              <div>
                <span className="font-semibold">Parameters:</span>
                <ul className="list-disc list-inside ml-4 mt-2 space-y-1">
                  <li>
                    <code className="bg-white px-2 py-1 rounded text-xs">msg</code> (optional):
                    표시할 메시지
                  </li>
                  <li>
                    <code className="bg-white px-2 py-1 rounded text-xs">error</code> (optional):
                    true/1 이면 오류 모드
                  </li>
                </ul>
              </div>
              <div>
                <span className="font-semibold">Response:</span>{' '}
                <code className="bg-white px-2 py-1 rounded text-xs">
                  text/html (자동으로 창을 닫는 HTML 페이지)
                </code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
