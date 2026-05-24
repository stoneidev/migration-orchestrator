package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import com.silicon2.admin.ambassador.my_page.domain.model.Review;
import com.silicon2.admin.ambassador.my_page.domain.repository.ReviewRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Repository
@RequiredArgsConstructor
public class ReviewRepositoryImpl implements ReviewRepository {

    private final ReviewJpaRepository jpaRepository;
    private final PersistenceMapper mapper;

    @Override
    public Review save(Review review) {
        ReviewEntity entity = mapper.toEntity(review);
        ReviewEntity saved = jpaRepository.save(entity);
        return mapper.toDomain(saved);
    }

    @Override
    public Optional<Review> findByCampaignIdAndAmbassadorMemberId(Long campaignId, Long ambassadorMemberId) {
        return jpaRepository.findByCampaignIdAndAmbassadorMemberId(campaignId, ambassadorMemberId)
                .map(mapper::toDomain);
    }

    @Override
    public List<Review> findByAmbassadorMemberId(Long ambassadorMemberId) {
        return jpaRepository.findByAmbassadorMemberId(ambassadorMemberId)
                .stream()
                .map(mapper::toDomain)
                .collect(Collectors.toList());
    }
}
