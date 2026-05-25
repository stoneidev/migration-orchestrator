'use client';

import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';
import AlertPopup from './components/AlertPopup';
import { mockAlertData } from './mock-data';

function AlertCloseContent() {
  const searchParams = useSearchParams();

  const message = searchParams.get('message') || searchParams.get('msg') || mockAlertData.message;
  const error = searchParams.get('error') || searchParams.get('err');
  const isError = error === '1' || error === 'true' || searchParams.get('type') === 'error';

  return <AlertPopup message={message} isError={isError} />;
}

export default function AlertClosePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-gray-600">로딩 중...</div>
        </div>
      }
    >
      <AlertCloseContent />
    </Suspense>
  );
}
