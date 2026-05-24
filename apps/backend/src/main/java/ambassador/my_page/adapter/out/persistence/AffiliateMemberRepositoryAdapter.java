package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.mapper.AffiliateMemberMapper;
import com.silicon2.admin.ambassador.my_page.domain.model.AffiliateMember;
import com.silicon2.admin.ambassador.my_page.domain.repository.AffiliateMemberRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class AffiliateMemberRepositoryAdapter implements AffiliateMemberRepository {

    private final AffiliateMemberJpaRepository jpaRepository;
    private final AffiliateMemberMapper mapper;

    @Override
    public Optional<AffiliateMember> findByMemberId(Long memberId) {
        return jpaRepository.findByMemberId(memberId)
            .map(mapper::toDomain);
    }

    @Override
    public AffiliateMember save(AffiliateMember affiliateMember) {
        return mapper.toDomain(
            jpaRepository.save(mapper.toEntity(affiliateMember))
        );
    }
}
