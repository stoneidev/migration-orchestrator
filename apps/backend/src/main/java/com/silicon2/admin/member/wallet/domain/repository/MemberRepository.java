package com.silicon2.admin.member.wallet.domain.repository;

import com.silicon2.admin.member.wallet.domain.model.Member;
import java.util.Optional;

public interface MemberRepository {
    Optional<Member> findByMbId(String mbId);
}
