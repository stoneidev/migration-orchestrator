package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.entity.AmbassadorCampaignImageEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface AmbassadorCampaignImageJpaRepository extends JpaRepository<AmbassadorCampaignImageEntity, Long> {
    List<AmbassadorCampaignImageEntity> findByAmbassadorMemberIdAndCampaignId(Long ambassadorMemberId, Long campaignId);
    int countByAmbassadorMemberIdAndCampaignId(Long ambassadorMemberId, Long campaignId);
}
