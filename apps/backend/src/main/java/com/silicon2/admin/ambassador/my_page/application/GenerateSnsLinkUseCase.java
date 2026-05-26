package com.silicon2.admin.ambassador.my_page.application;

import com.silicon2.admin.ambassador.my_page.application.dto.GenerateSnsLinkRequest;
import com.silicon2.admin.ambassador.my_page.application.dto.GenerateSnsLinkResponse;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberRepository;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberSnsRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class GenerateSnsLinkUseCase {

    private final AmbassadorMemberRepository ambassadorMemberRepository;
    private final AmbassadorMemberSnsRepository ambassadorMemberSnsRepository;

    public GenerateSnsLinkResponse execute(GenerateSnsLinkRequest request) {
        AmbassadorMember member = ambassadorMemberRepository.findByMemberId(request.getMemberId())
                .orElseThrow(() -> new IllegalArgumentException("Ambassador not found"));

        member.requireActiveForSnsLink();
        member.requireRegisteredSns(ambassadorMemberSnsRepository.findByAmbassadorMemberId(member.getId()));

        return GenerateSnsLinkResponse.builder()
                .shareUrl(member.generateCampaignLink(request.getCampaignId()))
                .trackingCode(member.getTrackingCode())
                .build();
    }
}
