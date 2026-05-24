package com.silicon2.admin.ambassador.my_page.domain.service;

import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AffiliateMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMemberSns;
import com.silicon2.admin.ambassador.my_page.domain.model.Campaign;
import com.silicon2.admin.ambassador.my_page.domain.model.Review;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AmbassadorDomainService {

    public void validateAmbassadorAccess(AmbassadorMember member) {
        if (!member.canAccessMyPage()) {
            throw new IllegalStateException("Ambassador cannot access my page: inactive or banned");
        }
    }

    public void validateReviewSubmission(Campaign campaign, AmbassadorMember member, Review existingReview) {
        if (!campaign.isActive()) {
            throw new IllegalStateException("Reviews can only be submitted during active campaign period");
        }

        if (existingReview != null) {
            throw new IllegalStateException("Only one review per campaign is allowed");
        }
    }

    public void validateReviewImages(List<String> imageUrls) {
        if (imageUrls != null && imageUrls.size() > 5) {
            throw new IllegalStateException("Maximum 5 images allowed per review");
        }
    }

    public void validateSnsLinkGeneration(List<AmbassadorMemberSns> snsList, AffiliateMember affiliateMember) {
        if (snsList == null || snsList.isEmpty()) {
            throw new IllegalStateException("At least one SNS account must be registered");
        }

        if (affiliateMember == null) {
            throw new IllegalStateException("Ambassador must have linked affiliate member to generate tracking links");
        }
    }

    public String generateTrackingLink(String baseUrl, String trackingCode) {
        String uniqueCode = trackingCode + "-" + UUID.randomUUID().toString().substring(0, 8);
        return baseUrl + "?ref=" + uniqueCode;
    }
}
