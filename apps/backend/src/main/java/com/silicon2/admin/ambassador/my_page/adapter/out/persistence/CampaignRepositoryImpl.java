package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import com.silicon2.admin.ambassador.my_page.domain.model.Campaign;
import com.silicon2.admin.ambassador.my_page.domain.repository.CampaignRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
@RequiredArgsConstructor
public class CampaignRepositoryImpl implements CampaignRepository {

    private final CampaignJpaRepository jpaRepository;
    private final PersistenceMapper mapper;

    @Override
    public Optional<Campaign> findById(Long id) {
        return jpaRepository.findById(id)
                .map(mapper::toDomain);
    }
}
