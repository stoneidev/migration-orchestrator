package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.mapper.AmbassadorCampaignImageMapper;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorCampaignImage;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorCampaignImageRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.stream.Collectors;

@Repository
@RequiredArgsConstructor
public class AmbassadorCampaignImageRepositoryAdapter implements AmbassadorCampaignImageRepository {

    private final AmbassadorCampaignImageJpaRepository jpaRepository;
    private final AmbassadorCampaignImageMapper mapper;

    @Override
    public List<AmbassadorCampaignImage> findByAmbassadorMemberIdAndCampaignId(Long ambassadorMemberId, Long campaignId) {
        return jpaRepository.findByAmbassadorMemberIdAndCampaignId(ambassadorMemberId, campaignId).stream()
            .map(mapper::toDomain)
            .collect(Collectors.toList());
    }

    @Override
    public List<AmbassadorCampaignImage> saveAll(List<AmbassadorCampaignImage> images) {
        return jpaRepository.saveAll(
            images.stream()
                .map(mapper::toEntity)
                .collect(Collectors.toList())
        ).stream()
            .map(mapper::toDomain)
            .collect(Collectors.toList());
    }

    @Override
    public int countByAmbassadorMemberIdAndCampaignId(Long ambassadorMemberId, Long campaignId) {
        return jpaRepository.countByAmbassadorMemberIdAndCampaignId(ambassadorMemberId, campaignId);
    }
}
