'use client';

import { useState, useEffect } from 'react';
import WalletHeader from './components/WalletHeader';
import WalletSummaryCards from './components/WalletSummaryCards';
import TransactionTabs from './components/TransactionTabs';
import PointTransactionList from './components/PointTransactionList';
import CouponList from './components/CouponList';
import BottomNavigation from './components/BottomNavigation';
import ChatButton from './components/ChatButton';
import { fetchWalletData } from './api';
import {
  mockWalletSummary,
  mockPointTransactions,
  mockCoupons,
} from './mock-data';
import { TransactionType, WalletSummary, PointTransaction, CouponItem } from './types';

export default function WalletPage() {
  const [activeTab, setActiveTab] = useState<TransactionType>('point');
  const [summary, setSummary] = useState<WalletSummary>(mockWalletSummary);
  const [points, setPoints] = useState<PointTransaction[]>(mockPointTransactions);
  const [coupons, setCoupons] = useState<CouponItem[]>(mockCoupons);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWalletData().then((data) => {
      setSummary(data.summary);
      setPoints(data.pointTransactions);
      setCoupons(data.coupons);
      setLoading(false);
    });
  }, []);

  return (
    <div className="min-h-screen bg-white max-w-[430px] mx-auto relative pb-20">
      <WalletHeader />

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="w-6 h-6 border-2 border-black border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <>
          <WalletSummaryCards summary={summary} />

          <TransactionTabs activeTab={activeTab} onTabChange={setActiveTab} />

          <div className="min-h-[400px]">
            {activeTab === 'point' ? (
              <PointTransactionList transactions={points} />
            ) : (
              <CouponList coupons={coupons} />
            )}
          </div>
        </>
      )}

      <ChatButton />
      <BottomNavigation />
    </div>
  );
}
