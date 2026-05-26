package com.silicon2.admin.shop.mp_profile.adapter.out.persistence;

import com.silicon2.admin.shop.mp_profile.adapter.out.persistence.mapper.BeautyProfileMapper;
import com.silicon2.admin.shop.mp_profile.domain.model.BeautyProfile;
import com.silicon2.admin.shop.mp_profile.domain.repository.BeautyProfileRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class BeautyProfileRepositoryAdapter implements BeautyProfileRepository {

    private final BeautyProfileJpaRepository jpaRepository;
    private final BeautyProfileMapper mapper;

    @Override
    public Optional<BeautyProfile> findByUserId(String userId) {
        return jpaRepository.findByUserId(userId).map(mapper::toDomain);
    }

    @Override
    public BeautyProfile save(BeautyProfile profile) {
        return mapper.toDomain(jpaRepository.save(mapper.toEntity(profile)));
    }

    @Override
    public long count() {
        return jpaRepository.count();
    }
}
