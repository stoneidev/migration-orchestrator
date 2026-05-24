package com.silicon2.admin.ambassador.my_page.application.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReviewSubmitRequest {
    private Long campaignId;
    private String content;
    private Integer rating;
    private List<String> imageUrls;
}
