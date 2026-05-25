'use client';

import { CouponItem } from '../types';

interface CouponListProps {
  coupons: CouponItem[];
}

export default function CouponList({ coupons }: CouponListProps) {
  if (coupons.length === 0) {
    return (
      <div className="bg-white px-4 py-12 text-center text-gray-400">
        No coupons available
      </div>
    );
  }

  return (
    <div className="bg-white">
      {coupons.map((coupon) => (
        <div
          key={coupon.id}
          className="px-4 py-5 border-b border-gray-100 last:border-b-0"
        >
          <div className="flex justify-between items-start mb-1">
            <div className="flex-1">
              <div className="text-sm text-gray-500 mb-1">{coupon.date}</div>
              <div className="text-base font-medium text-black mb-1">
                {coupon.title}
              </div>
              <div className="text-xs text-gray-400">
                {coupon.validFrom} ~ {coupon.validTo}
              </div>
            </div>
            <div className="text-base font-medium text-pink-500">
              {coupon.discount}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
