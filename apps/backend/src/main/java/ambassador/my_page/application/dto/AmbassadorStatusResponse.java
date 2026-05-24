package com.silicon2.admin.ambassador.my_page.application.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AmbassadorStatusResponse {
    private Long ambassadorId;
    private String status;
    private Boolean isActive;
    private LocalDateTime approvedAt;
    private Integer snsAccountCount;
    private Boolean hasAffiliateLink;
    private String trackingCode;
}
