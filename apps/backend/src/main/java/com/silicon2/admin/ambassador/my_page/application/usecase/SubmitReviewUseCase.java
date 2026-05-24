package com.silicon2.admin.ambassador.my_page.application.usecase;

import com.silicon2.admin.ambassador.my_page.application.dto.ReviewSubmitRequest;
import com.silicon2.admin.ambassador.my_page.application.dto.ReviewSubmitResponse;
import com.silicon2.admin.ambassador.my_page.application.mapper.AmbassadorMapper;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.model.Campaign;
import com.silicon2.admin.ambassador.my_page.domain.model.Review;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberRepository;
import com.silicon2.admin.ambassador.my_page.domain.repository.CampaignRepository;
import com.silicon2.admin.ambassador.my_page.domain.repository.ReviewRepository;
import com.silicon2.admin.ambassador.my_page.domain.service.AmbassadorDomainService;
import com.silicon2.admin.common.exception.BusinessException;
import com.silicon2.admin.common.exception.ErrorCode;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class SubmitReviewUseCase {

    private final AmbassadorMemberRepository ambassadorMemberRepository;
    private final CampaignRepository campaignRepository;
    private final ReviewRepository reviewRepository;
    private final AmbassadorDomainService ambassadorDomainService;
    private final AmbassadorMapper ambassadorMapper;

    @Transactional
    public ReviewSubmitResponse execute(Long ambassadorId, ReviewSubmitRequest request) {
        AmbassadorMember member = ambassadorMemberRepository.findById(ambassadorId)
                .orElseThrow(() -> new BusinessException(ErrorCode.ENTITY_NOT_FOUND));

        ambassadorDomainService.validateAmbassadorAccess(member);

        Campaign campaign = campaignRepository.findById(request.getCampaignId())
                .orElseThrow(() -> new BusinessException(ErrorCode.ENTITY_NOT_FOUND));

        Review existingReview = reviewRepository
                .findByCampaignIdAndAmbassadorMemberId(request.getCampaignId(), ambassadorId)
                .orElse(null);

        ambassadorDomainService.validateReviewSubmission(campaign, member, existingReview);
        ambassadorDomainService.validateReviewImages(request.getImageUrls());

        Review review = Review.builder()
                .campaignId(request.getCampaignId())
                .ambassadorMemberId(ambassadorId)
                .content(request.getContent())
                .rating(request.getRating())
                .imageUrls(request.getImageUrls())
                .status("PENDING")
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        Review savedReview = reviewRepository.save(review);

        return ambassadorMapper.toReviewSubmitResponse(savedReview);
    }
}
