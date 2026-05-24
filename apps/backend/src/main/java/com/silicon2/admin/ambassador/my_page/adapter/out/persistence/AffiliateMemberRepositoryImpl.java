package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import com.silicon2.admin.ambassador.my_page.domain.model.AffiliateMember;
import com.silicon2.admin.ambassador.my_page.domain.repository.AffiliateMemberRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class AffiliateMemberRepositoryImpl implements AffiliateMemberRepository {

    private final AffiliateMemberJpaRepository jpaRepository;
    private final PersistenceMapper mapper;

    @Override
    public Optional<AffiliateMember> findByAmbassadorMemberId(Long ambassadorMemberId) {
        return jpaRepository.findByAmbassadorMemberId(ambassadorMemberId)
                .map(mapper::toDomain);
    }

    @Override
    public AffiliateMember save(AffiliateMember affiliateMember) {
        AffiliateMemberEntity entity = mapper.toEntity(affiliateMember);
        AffiliateMemberEntity saved = jpaRepository.save(entity);
        return mapper.toDomain(saved);
    }
}
