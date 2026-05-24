package com.silicon2.admin.ambassador.my_page.domain.model;

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
public class Review {
    private Long id;
    private Long campaignId;
    private Long ambassadorMemberId;
    private String content;
    private Integer rating;
    private List<String> imageUrls;
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public boolean hasValidImageCount() {
        return imageUrls == null || imageUrls.size() <= 5;
    }
}
