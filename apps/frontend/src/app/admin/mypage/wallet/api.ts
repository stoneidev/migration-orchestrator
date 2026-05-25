import { WalletSummary, PointTransaction, CouponItem } from './types';
import { mockWalletSummary, mockPointTransactions, mockCoupons } from './mock-data';

const API_BASE_URL = 'http://localhost:8080/api/v1/member/wallet';

export async function fetchWalletData(): Promise<{
  summary: WalletSummary;
  pointTransactions: PointTransaction[];
  coupons: CouponItem[];
}> {
  try {
    const response = await fetch(API_BASE_URL, {
      signal: AbortSignal.timeout(3000),
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const json = await response.json();
    const data = json.data || json;

    const points = data.member?.mbPoint ?? 0;
    const couponCount = data.couponStatus?.couponCount ?? 0;

    return {
      summary: { points, coupons: couponCount },
      pointTransactions: (data.pointTransactions || mockPointTransactions).map((t: any) => ({
        id: String(t.id),
        date: t.date,
        title: t.title,
        amount: t.amount,
        validFrom: t.validFrom,
        validTo: t.validTo,
      })),
      coupons: (data.couponItems || mockCoupons).map((c: any) => ({
        id: String(c.id),
        date: c.date,
        title: c.title,
        discount: c.discount,
        validFrom: c.validFrom,
        validTo: c.validTo,
      })),
    };
  } catch (error) {
    console.warn('Backend unavailable, using mock data:', error);
    return {
      summary: mockWalletSummary,
      pointTransactions: mockPointTransactions,
      coupons: mockCoupons,
    };
  }
}
