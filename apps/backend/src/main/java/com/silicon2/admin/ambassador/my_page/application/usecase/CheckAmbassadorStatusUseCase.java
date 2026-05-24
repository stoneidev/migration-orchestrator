package com.silicon2.admin.ambassador.my_page.application.usecase;

import com.silicon2.admin.ambassador.my_page.application.dto.AmbassadorStatusResponse;
import com.silicon2.admin.ambassador.my_page.application.mapper.AmbassadorMapper;
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
public class CheckAmbassadorStatusUseCase {

    private final AmbassadorMemberRepository ambassadorMemberRepository;
    private final AmbassadorMemberSnsRepository ambassadorMemberSnsRepository;
    private final AffiliateMemberRepository affiliateMemberRepository;
    private final AmbassadorDomainService ambassadorDomainService;
    private final AmbassadorMapper ambassadorMapper;

    @Transactional(readOnly = true)
    public AmbassadorStatusResponse execute(Long ambassadorId) {
        AmbassadorMember member = ambassadorMemberRepository.findById(ambassadorId)
                .orElseThrow(() -> new BusinessException(ErrorCode.ENTITY_NOT_FOUND));

        ambassadorDomainService.validateAmbassadorAccess(member);

        List<AmbassadorMemberSns> snsList = ambassadorMemberSnsRepository
                .findByAmbassadorMemberId(ambassadorId);

        AffiliateMember affiliateMember = affiliateMemberRepository
                .findByAmbassadorMemberId(ambassadorId)
                .orElse(null);

        AmbassadorStatusResponse response = ambassadorMapper.toStatusResponse(member);
        response.setHasAffiliate(affiliateMember != null && affiliateMember.getIsActive());
        response.setSnsAccounts(ambassadorMapper.toSnsAccountDtoList(snsList));

        return response;
    }
}
