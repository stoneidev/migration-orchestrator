package com.silicon2.admin.ambassador.my_page.domain.service;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class ReviewSubmissionService {

    public void validateReviewSubmission(Long campaignId, LocalDateTime campaignStartDate, LocalDateTime campaignEndDate, int existingImageCount, int newImageCount) {
        LocalDateTime now = LocalDateTime.now();

        if (now.isBefore(campaignStartDate) || now.isAfter(campaignEndDate)) {
            throw new IllegalStateException("Reviews can only be submitted during the campaign active period");
        }

        if (existingImageCount > 0) {
            throw new IllegalStateException("Review already submitted for this campaign");
        }

        if (newImageCount > 5) {
            throw new IllegalStateException("Maximum of 5 images allowed per review");
        }

        if (newImageCount < 1) {
            throw new IllegalStateException("At least one image is required");
        }
    }
}
