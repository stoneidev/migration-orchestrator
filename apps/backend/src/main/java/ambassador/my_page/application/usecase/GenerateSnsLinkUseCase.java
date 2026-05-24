package com.silicon2.admin.ambassador.my_page.application.usecase;

import com.silicon2.admin.ambassador.my_page.application.dto.GenerateSnsLinkRequest;
import com.silicon2.admin.ambassador.my_page.application.dto.GenerateSnsLinkResponse;
import com.silicon2.admin.ambassador.my_page.domain.model.AffiliateMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMemberSns;
import com.silicon2.admin.ambassador.my_page.domain.repository.AffiliateMemberRepository;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberRepository;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberSnsRepository;
import com.silicon2.admin.ambassador.my_page.domain.service.AmbassadorStatusService;
import com.silicon2.admin.ambassador.my_page.domain.service.SnsLinkGenerationService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class GenerateSnsLinkUseCase {

    private final AmbassadorMemberRepository ambassadorMemberRepository;
    private final AmbassadorMemberSnsRepository ambassadorMemberSnsRepository;
    private final AffiliateMemberRepository affiliateMemberRepository;
    private final AmbassadorStatusService ambassadorStatusService;
    private final SnsLinkGenerationService snsLinkGenerationService;

    @Transactional
    public GenerateSnsLinkResponse execute(Long memberId, GenerateSnsLinkRequest request) {
        AmbassadorMember ambassador = ambassadorMemberRepository.findByMemberId(memberId)
            .orElseThrow(() -> new IllegalArgumentException("Ambassador not found"));

        ambassadorStatusService.validateAccess(ambassador);

        List<AmbassadorMemberSns> snsList = ambassadorMemberSnsRepository.findByAmbassadorMemberId(ambassador.getId());
        snsLinkGenerationService.validateSnsAccountExists(snsList.size());

        AffiliateMember affiliate = affiliateMemberRepository.findByMemberId(memberId).orElse(null);

        String trackingLink = snsLinkGenerationService.generateTrackingLink(
            affiliate,
            request.getBaseUrl(),
            request.getCampaignId()
        );

        return GenerateSnsLinkResponse.builder()
            .trackingLink(trackingLink)
            .trackingCode(affiliate != null ? affiliate.getTrackingCode() : null)
            .campaignId(request.getCampaignId())
            .generatedAt(java.time.LocalDateTime.now())
            .build();
    }
}
