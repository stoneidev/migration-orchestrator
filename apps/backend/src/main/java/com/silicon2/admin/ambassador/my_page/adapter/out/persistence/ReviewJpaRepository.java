package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface ReviewJpaRepository extends JpaRepository<ReviewEntity, Long> {
    Optional<ReviewEntity> findByCampaignIdAndAmbassadorMemberId(Long campaignId, Long ambassadorMemberId);
    List<ReviewEntity> findByAmbassadorMemberId(Long ambassadorMemberId);
}
