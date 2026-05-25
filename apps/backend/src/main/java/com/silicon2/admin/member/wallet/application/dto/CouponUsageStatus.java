package com.silicon2.admin.member.wallet.application.dto;

import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CouponUsageStatus {
    private String mbId;
    private Boolean hasUsedCoupon;
    private Integer couponCount;
}
