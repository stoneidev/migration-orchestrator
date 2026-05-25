'use client';

import { useEffect } from 'react';

interface AlertPopupProps {
  message: string;
  isError: boolean;
}

export default function AlertPopup({ message, isError }: AlertPopupProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      if (typeof window !== 'undefined') {
        window.close();
        setTimeout(() => {
          if (!window.closed && window.opener) {
            window.opener.focus();
          }
        }, 100);
      }
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const messageLines = message.split(/\\n|\n/).filter(line => line.trim());

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-[380px] overflow-hidden">
        <div
          className={`px-6 py-4 ${
            isError
              ? 'bg-gradient-to-r from-red-500 to-red-600'
              : 'bg-gradient-to-r from-blue-500 to-blue-600'
          }`}
        >
          <div className="flex items-center gap-3">
            {isError ? (
              <svg
                className="w-7 h-7 text-white flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            ) : (
              <svg
                className="w-7 h-7 text-white flex-shrink-0"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            )}
            <h2 className="text-white text-lg font-bold">
              {isError ? '오류' : '알림'}
            </h2>
          </div>
        </div>

        <div className="px-6 py-8">
          <div className="text-center space-y-2">
            {messageLines.map((line, index) => (
              <p
                key={index}
                className="text-gray-800 text-[15px] leading-relaxed"
              >
                {line}
              </p>
            ))}
          </div>
        </div>

        <div className="px-6 pb-6">
          <button
            onClick={() => window.close()}
            className={`w-full py-3 px-4 rounded-md text-white font-semibold transition-all duration-200 shadow-md hover:shadow-lg active:scale-95 ${
              isError
                ? 'bg-red-500 hover:bg-red-600'
                : 'bg-blue-500 hover:bg-blue-600'
            }`}
          >
            확인
          </button>
        </div>

        <div className="px-6 pb-4">
          <p className="text-center text-xs text-gray-400">
            이 창은 자동으로 닫힙니다
          </p>
        </div>
      </div>

      <noscript>
        <div className="fixed inset-0 bg-white flex items-center justify-center p-4 z-50">
          <div className="text-center max-w-md">
            <h1 className="text-xl font-bold text-gray-900 mb-4">
              {isError ? '오류' : '알림'}
            </h1>
            <div className="space-y-2 mb-6">
              {messageLines.map((line, i) => (
                <p key={i} className="text-gray-700">
                  {line}
                </p>
              ))}
            </div>
            <p className="text-sm text-gray-500 border-t pt-4">
              JavaScript가 비활성화되어 있습니다.<br />
              이 창을 수동으로 닫아주세요.
            </p>
          </div>
        </div>
      </noscript>
    </div>
  );
}
