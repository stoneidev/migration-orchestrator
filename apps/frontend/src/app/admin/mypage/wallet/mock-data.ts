import { WalletSummary, PointTransaction, CouponItem } from './types';

export const mockWalletSummary: WalletSummary = {
  points: 5.0,
  coupons: 1,
};

export const mockPointTransactions: PointTransaction[] = [
  {
    id: '1',
    date: '2026.04.16',
    title: 'point expired',
    amount: -5.0,
    validFrom: '2026.04.16',
    validTo: '2026.04.16',
  },
  {
    id: '2',
    date: '2026.04.14',
    title: '24 Hours Surprise Credit',
    amount: 5.0,
    validFrom: '2026.04.14',
    validTo: '2026.04.15',
  },
  {
    id: '3',
    date: '2026.03.25',
    title: 'New member',
    amount: 5.0,
    validFrom: '2026.03.25',
    validTo: '2026.09.20',
  },
];

export const mockCoupons: CouponItem[] = [];
