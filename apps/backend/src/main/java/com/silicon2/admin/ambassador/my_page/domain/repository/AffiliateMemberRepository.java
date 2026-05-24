package com.silicon2.admin.ambassador.my_page.domain.repository;

import com.silicon2.admin.ambassador.my_page.domain.model.AffiliateMember;

import java.util.Optional;

public interface AffiliateMemberRepository {
    Optional<AffiliateMember> findByAmbassadorMemberId(Long ambassadorMemberId);
    AffiliateMember save(AffiliateMember affiliateMember);
}
