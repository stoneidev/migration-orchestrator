package com.silicon2.admin.member.wallet.application.dto;

import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class WalletData {
    private MemberInfo member;
    private AffiliateInfo affiliate;
    private CouponUsageStatus couponStatus;
}
