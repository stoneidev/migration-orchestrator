package com.silicon2.admin.member.wallet.domain.model;

import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Member {
    private Long id;
    private String mbId;
    private Integer mbPoint;
    private String mbName;
    private String mbEmail;
    private Boolean hasUsedCoupon;
    private Integer couponCount;
}
