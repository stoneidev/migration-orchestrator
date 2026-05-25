package com.silicon2.admin.member.wallet.adapter.out.persistence;

import com.silicon2.admin.member.wallet.adapter.out.persistence.entity.MemberWalletEntity;
import com.silicon2.admin.member.wallet.adapter.out.persistence.mapper.MemberMapper;
import com.silicon2.admin.member.wallet.domain.model.Member;
import com.silicon2.admin.member.wallet.domain.repository.MemberRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class MemberRepositoryAdapter implements MemberRepository {

    private final MemberJpaRepository jpaRepository;
    private final MemberMapper mapper;

    @Override
    public Optional<Member> findByMbId(String mbId) {
        return jpaRepository.findByMbId(mbId)
                .map(mapper::toDomain);
    }
}
