package com.silicon2.admin.ambassador.my_page.domain.repository;

import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorCampaignImage;

import java.util.List;

public interface AmbassadorCampaignImageRepository {
    List<AmbassadorCampaignImage> findByAmbassadorMemberIdAndCampaignId(Long ambassadorMemberId, Long campaignId);
    List<AmbassadorCampaignImage> saveAll(List<AmbassadorCampaignImage> images);
    int countByAmbassadorMemberIdAndCampaignId(Long ambassadorMemberId, Long campaignId);
}
