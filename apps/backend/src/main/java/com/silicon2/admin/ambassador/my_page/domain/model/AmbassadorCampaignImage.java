package com.silicon2.admin.ambassador.my_page.domain.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AmbassadorCampaignImage {
    private Long id;
    private Long campaignId;
    private Long ambassadorMemberId;
    private String imageUrl;
    private String imageType;
    private Integer displayOrder;
    private LocalDateTime createdAt;
}
