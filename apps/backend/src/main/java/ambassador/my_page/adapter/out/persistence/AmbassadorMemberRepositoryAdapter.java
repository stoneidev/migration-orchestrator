package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.mapper.AmbassadorMemberMapper;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class AmbassadorMemberRepositoryAdapter implements AmbassadorMemberRepository {

    private final AmbassadorMemberJpaRepository jpaRepository;
    private final AmbassadorMemberMapper mapper;

    @Override
    public Optional<AmbassadorMember> findById(Long id) {
        return jpaRepository.findById(id)
            .map(mapper::toDomain);
    }

    @Override
    public Optional<AmbassadorMember> findByMemberId(Long memberId) {
        return jpaRepository.findByMemberId(memberId)
            .map(mapper::toDomain);
    }

    @Override
    public AmbassadorMember save(AmbassadorMember ambassadorMember) {
        return mapper.toDomain(
            jpaRepository.save(mapper.toEntity(ambassadorMember))
        );
    }
}
