package com.silicon2.admin.ambassador.my_page.application;

import com.silicon2.admin.ambassador.my_page.application.dto.AmbassadorStatusResponse;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorStatus;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class CheckAmbassadorStatusUseCase {

    private final AmbassadorMemberRepository ambassadorMemberRepository;

    public AmbassadorStatusResponse execute(Long memberId) {
        AmbassadorMember member = ambassadorMemberRepository.findByMemberId(memberId)
                .orElseThrow(() -> new IllegalArgumentException("Ambassador not found"));

        return AmbassadorStatusResponse.builder()
                .memberId(member.getMemberId())
                .status(member.getStatus())
                .trackingCode(member.getTrackingCode())
                .canAccess(member.getStatus() == AmbassadorStatus.ACTIVE)
                .build();
    }
}
