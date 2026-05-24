package com.silicon2.admin.ambassador.my_page.application.usecase;

import com.silicon2.admin.ambassador.my_page.application.dto.SnsLinkRequest;
import com.silicon2.admin.ambassador.my_page.application.dto.SnsLinkResponse;
import com.silicon2.admin.ambassador.my_page.domain.model.AffiliateMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMemberSns;
import com.silicon2.admin.ambassador.my_page.domain.repository.AffiliateMemberRepository;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberRepository;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberSnsRepository;
import com.silicon2.admin.ambassador.my_page.domain.service.AmbassadorDomainService;
import com.silicon2.admin.common.exception.BusinessException;
import com.silicon2.admin.common.exception.ErrorCode;
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
    private final AmbassadorDomainService ambassadorDomainService;

    @Transactional(readOnly = true)
    public SnsLinkResponse execute(Long ambassadorId, SnsLinkRequest request) {
        AmbassadorMember member = ambassadorMemberRepository.findById(ambassadorId)
                .orElseThrow(() -> new BusinessException(ErrorCode.ENTITY_NOT_FOUND));

        ambassadorDomainService.validateAmbassadorAccess(member);

        List<AmbassadorMemberSns> snsList = ambassadorMemberSnsRepository
                .findByAmbassadorMemberId(ambassadorId);

        AffiliateMember affiliateMember = affiliateMemberRepository
                .findByAmbassadorMemberId(ambassadorId)
                .orElse(null);

        ambassadorDomainService.validateSnsLinkGeneration(snsList, affiliateMember);

        String trackingUrl = ambassadorDomainService.generateTrackingLink(
                request.getBaseUrl(),
                affiliateMember.getTrackingCode()
        );

        return SnsLinkResponse.builder()
                .trackingUrl(trackingUrl)
                .trackingCode(affiliateMember.getTrackingCode())
                .snsType(request.getSnsType())
                .build();
    }
}
