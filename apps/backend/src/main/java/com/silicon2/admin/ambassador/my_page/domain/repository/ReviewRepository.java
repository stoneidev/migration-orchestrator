package com.silicon2.admin.ambassador.my_page.domain.repository;

import com.silicon2.admin.ambassador.my_page.domain.model.Review;

import java.util.List;
import java.util.Optional;

public interface ReviewRepository {
    Review save(Review review);
    Optional<Review> findByCampaignIdAndAmbassadorMemberId(Long campaignId, Long ambassadorMemberId);
    List<Review> findByAmbassadorMemberId(Long ambassadorMemberId);
}
