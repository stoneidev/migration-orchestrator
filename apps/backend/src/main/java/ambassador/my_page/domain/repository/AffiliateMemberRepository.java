package com.silicon2.admin.ambassador.my_page.domain.repository;

import com.silicon2.admin.ambassador.my_page.domain.model.AffiliateMember;

import java.util.Optional;

public interface AffiliateMemberRepository {
    Optional<AffiliateMember> findByMemberId(Long memberId);
    AffiliateMember save(AffiliateMember affiliateMember);
}
