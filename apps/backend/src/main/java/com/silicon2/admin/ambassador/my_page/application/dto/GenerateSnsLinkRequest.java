package com.silicon2.admin.ambassador.my_page.application.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GenerateSnsLinkRequest {
    private Long memberId;
    private Long campaignId;
    private String snsType;
}
