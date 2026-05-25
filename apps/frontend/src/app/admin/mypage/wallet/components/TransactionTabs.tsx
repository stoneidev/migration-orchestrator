'use client';

import { TransactionType } from '../types';

interface TransactionTabsProps {
  activeTab: TransactionType;
  onTabChange: (tab: TransactionType) => void;
}

export default function TransactionTabs({
  activeTab,
  onTabChange,
}: TransactionTabsProps) {
  return (
    <div className="bg-white border-b border-gray-200">
      <div className="flex">
        <button
          onClick={() => onTabChange('point')}
          className={`flex-1 py-4 text-center font-medium transition-colors ${
            activeTab === 'point'
              ? 'text-black border-b-2 border-black'
              : 'text-gray-400'
          }`}
        >
          Point
        </button>
        <button
          onClick={() => onTabChange('coupon')}
          className={`flex-1 py-4 text-center font-medium transition-colors ${
            activeTab === 'coupon'
              ? 'text-black border-b-2 border-black'
              : 'text-gray-400'
          }`}
        >
          Coupon
        </button>
      </div>
    </div>
  );
}
