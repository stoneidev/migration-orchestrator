package com.silicon2.admin.ambassador.my_page.domain.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AmbassadorMember {
    private Long id;
    private Long memberId;
    private AmbassadorStatus status;
    private String trackingCode;
    private LocalDateTime joinedAt;
    private LocalDateTime updatedAt;

    public boolean isActive() {
        return status == AmbassadorStatus.ACTIVE;
    }

    public boolean canAccessPage() {
        return status == AmbassadorStatus.ACTIVE;
    }

    public static void validateReviewImageCount(List<String> imageUrls) {
        if (imageUrls != null && imageUrls.size() > 5) {
            throw new IllegalArgumentException("Maximum 5 images allowed");
        }
    }

    public void requireActiveForSnsLink() {
        if (!isActive()) {
            throw new IllegalStateException("Only active ambassadors can generate SNS links");
        }
    }

    public void requireActiveForReview() {
        if (!isActive()) {
            throw new IllegalStateException("Only active ambassadors can submit reviews");
        }
    }

    public void requireRegisteredSns(List<AmbassadorMemberSns> snsAccounts) {
        if (snsAccounts.isEmpty()) {
            throw new IllegalStateException("At least one SNS account must be registered");
        }
    }

    public String generateCampaignLink(Long campaignId) {
        return String.format("https://example.com/campaign/%d?ref=%s", campaignId, trackingCode);
    }
}
