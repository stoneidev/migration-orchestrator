'use client';

import { WalletSummary } from '../types';

interface WalletSummaryCardsProps {
  summary: WalletSummary;
}

export default function WalletSummaryCards({ summary }: WalletSummaryCardsProps) {
  return (
    <div className="px-4 py-6 bg-white">
      <div className="flex gap-3">
        <div className="flex-1 bg-gray-100 rounded-lg p-4">
          <div className="text-sm text-gray-500 mb-2">Point</div>
          <div className="text-2xl font-bold text-black">
            {summary.points.toFixed(2)} P
          </div>
        </div>
        <div className="flex-1 bg-gray-100 rounded-lg p-4">
          <div className="text-sm text-gray-500 mb-2">Coupon</div>
          <div className="text-2xl font-bold text-black">{summary.coupons}</div>
        </div>
      </div>
      <p className="text-xs text-gray-500 mt-4">
        The expiration time displayed is in KST.
      </p>
    </div>
  );
}
