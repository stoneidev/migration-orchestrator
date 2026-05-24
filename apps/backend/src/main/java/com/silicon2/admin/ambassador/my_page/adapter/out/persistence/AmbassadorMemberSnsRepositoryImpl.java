package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMemberSns;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberSnsRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
@RequiredArgsConstructor
public class AmbassadorMemberSnsRepositoryImpl implements AmbassadorMemberSnsRepository {

    private final AmbassadorMemberSnsJpaRepository jpaRepository;
    private final PersistenceMapper mapper;

    @Override
    public List<AmbassadorMemberSns> findByAmbassadorMemberId(Long ambassadorMemberId) {
        List<AmbassadorMemberSnsEntity> entities = jpaRepository.findByAmbassadorMemberId(ambassadorMemberId);
        return mapper.toDomainList(entities);
    }

    @Override
    public AmbassadorMemberSns save(AmbassadorMemberSns sns) {
        AmbassadorMemberSnsEntity entity = mapper.toEntity(sns);
        AmbassadorMemberSnsEntity saved = jpaRepository.save(entity);
        return mapper.toDomain(saved);
    }
}
