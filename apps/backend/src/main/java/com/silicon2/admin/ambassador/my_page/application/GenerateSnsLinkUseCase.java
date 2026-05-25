package com.silicon2.admin.ambassador.my_page.application;

import com.silicon2.admin.ambassador.my_page.application.dto.GenerateSnsLinkRequest;
import com.silicon2.admin.ambassador.my_page.application.dto.GenerateSnsLinkResponse;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMemberSns;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberRepository;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberSnsRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class GenerateSnsLinkUseCase {

    private final AmbassadorMemberRepository ambassadorMemberRepository;
    private final AmbassadorMemberSnsRepository ambassadorMemberSnsRepository;

    public GenerateSnsLinkResponse execute(GenerateSnsLinkRequest request) {
        AmbassadorMember member = ambassadorMemberRepository.findByMemberId(request.getMemberId())
                .orElseThrow(() -> new IllegalArgumentException("Ambassador not found"));

        // BR-001: Only active ambassadors can generate SNS links
        if (!member.isActive()) {
            throw new IllegalStateException("Only active ambassadors can generate SNS links");
        }

        // BR-008: At least one SNS account must be registered
        List<AmbassadorMemberSns> snsAccounts = ambassadorMemberSnsRepository
                .findByAmbassadorMemberId(member.getId());
        
        if (snsAccounts.isEmpty()) {
            throw new IllegalStateException("At least one SNS account must be registered");
        }

        // BR-004: Each SNS link generated must include a unique ambassador tracking code
        String snsLink = String.format("https://example.com/campaign/%d?ref=%s",
                request.getCampaignId(),
                member.getTrackingCode());

        return GenerateSnsLinkResponse.builder()
                .shareUrl(snsLink)
                .trackingCode(member.getTrackingCode())
                .build();
    }
}
