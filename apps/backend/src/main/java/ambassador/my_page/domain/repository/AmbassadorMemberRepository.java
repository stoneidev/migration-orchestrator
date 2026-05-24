package com.silicon2.admin.ambassador.my_page.domain.repository;

import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;

import java.util.Optional;

public interface AmbassadorMemberRepository {
    Optional<AmbassadorMember> findById(Long id);
    Optional<AmbassadorMember> findByMemberId(Long memberId);
    AmbassadorMember save(AmbassadorMember ambassadorMember);
}
