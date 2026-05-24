package com.silicon2.admin.ambassador.my_page.application.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SubmitReviewRequest {
    private Long campaignId;
    private List<String> imageUrls;
    private String reviewContent;
    private LocalDateTime campaignStartDate;
    private LocalDateTime campaignEndDate;
}
