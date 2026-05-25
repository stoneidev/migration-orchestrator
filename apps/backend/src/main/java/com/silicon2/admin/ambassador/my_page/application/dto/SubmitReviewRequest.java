package com.silicon2.admin.ambassador.my_page.application.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SubmitReviewRequest {
    private Long memberId;
    private Long campaignId;
    private String reviewContent;
    private List<String> imageUrls;
}
