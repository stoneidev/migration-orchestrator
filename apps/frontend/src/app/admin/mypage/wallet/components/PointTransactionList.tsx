'use client';

import { PointTransaction } from '../types';

interface PointTransactionListProps {
  transactions: PointTransaction[];
}

export default function PointTransactionList({
  transactions,
}: PointTransactionListProps) {
  return (
    <div className="bg-white px-4">
      {transactions.map((transaction) => (
        <div
          key={transaction.id}
          className="py-6 border-b border-gray-100 last:border-b-0"
        >
          <div className="text-sm text-gray-600 mb-1">{transaction.date}</div>
          <div className="flex justify-between items-start mb-2">
            <div className="text-base font-medium text-black">{transaction.title}</div>
            <div
              className={`text-base font-semibold ml-4 ${
                transaction.amount > 0 ? 'text-pink-500' : 'text-gray-400'
              }`}
            >
              {transaction.amount > 0 ? '+' : ''}
              {transaction.amount.toFixed(2)} P
            </div>
          </div>
          <div className="text-xs text-gray-400">
            {transaction.validFrom} - {transaction.validTo}
          </div>
        </div>
      ))}
    </div>
  );
}
