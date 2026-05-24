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
public class GenerateSnsLinkResponse {
    private String trackingLink;
    private String trackingCode;
    private Long campaignId;
    private LocalDateTime generatedAt;
}
