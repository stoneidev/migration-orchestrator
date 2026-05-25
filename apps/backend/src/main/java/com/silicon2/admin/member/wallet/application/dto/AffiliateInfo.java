package com.silicon2.admin.member.wallet.application.dto;

import lombok.*;
import java.math.BigDecimal;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AffiliateInfo {
    private String mbId;
    private Integer affiliateId;
    private BigDecimal commissionRate;
    private BigDecimal totalEarnings;
}
