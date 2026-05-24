package com.silicon2.admin.ambassador.my_page.application.usecase;

import com.silicon2.admin.ambassador.my_page.application.dto.AmbassadorStatusResponse;
import com.silicon2.admin.ambassador.my_page.domain.model.AffiliateMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMemberSns;
import com.silicon2.admin.ambassador.my_page.domain.repository.AffiliateMemberRepository;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberRepository;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberSnsRepository;
import com.silicon2.admin.ambassador.my_page.domain.service.AmbassadorStatusService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CheckAmbassadorStatusUseCase {

    private final AmbassadorMemberRepository ambassadorMemberRepository;
    private final AmbassadorMemberSnsRepository ambassadorMemberSnsRepository;
    private final AffiliateMemberRepository affiliateMemberRepository;
    private final AmbassadorStatusService ambassadorStatusService;

    @Transactional(readOnly = true)
    public AmbassadorStatusResponse execute(Long memberId) {
        AmbassadorMember ambassador = ambassadorMemberRepository.findByMemberId(memberId)
            .orElseThrow(() -> new IllegalArgumentException("Ambassador not found"));

        ambassadorStatusService.validateAccess(ambassador);

        List<AmbassadorMemberSns> snsList = ambassadorMemberSnsRepository.findByAmbassadorMemberId(ambassador.getId());
        AffiliateMember affiliate = affiliateMemberRepository.findByMemberId(memberId).orElse(null);

        return AmbassadorStatusResponse.builder()
            .ambassadorId(ambassador.getId())
            .status(ambassador.getStatus())
            .isActive(ambassador.isActive())
            .approvedAt(ambassador.getApprovedAt())
            .snsAccountCount(snsList.size())
            .hasAffiliateLink(affiliate != null)
            .trackingCode(affiliate != null ? affiliate.getTrackingCode() : null)
            .build();
    }
}
