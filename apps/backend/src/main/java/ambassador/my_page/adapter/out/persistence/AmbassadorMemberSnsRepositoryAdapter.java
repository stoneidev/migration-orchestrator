package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.mapper.AmbassadorMemberSnsMapper;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMemberSns;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberSnsRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.stream.Collectors;

@Repository
@RequiredArgsConstructor
public class AmbassadorMemberSnsRepositoryAdapter implements AmbassadorMemberSnsRepository {

    private final AmbassadorMemberSnsJpaRepository jpaRepository;
    private final AmbassadorMemberSnsMapper mapper;

    @Override
    public List<AmbassadorMemberSns> findByAmbassadorMemberId(Long ambassadorMemberId) {
        return jpaRepository.findByAmbassadorMemberId(ambassadorMemberId).stream()
            .map(mapper::toDomain)
            .collect(Collectors.toList());
    }

    @Override
    public AmbassadorMemberSns save(AmbassadorMemberSns sns) {
        return mapper.toDomain(
            jpaRepository.save(mapper.toEntity(sns))
        );
    }
}
