export interface WalletSummary {
  points: number;
  coupons: number;
}

export interface PointTransaction {
  id: string;
  date: string;
  title: string;
  amount: number;
  validFrom: string;
  validTo: string;
}

export interface CouponItem {
  id: string;
  date: string;
  title: string;
  discount: string;
  validFrom: string;
  validTo: string;
}

export type TransactionType = 'point' | 'coupon';
