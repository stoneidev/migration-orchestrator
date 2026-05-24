package com.silicon2.admin.ambassador.my_page.application.usecase;

import com.silicon2.admin.ambassador.my_page.application.dto.SubmitReviewRequest;
import com.silicon2.admin.ambassador.my_page.application.dto.SubmitReviewResponse;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorCampaignImage;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorCampaignImageRepository;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberRepository;
import com.silicon2.admin.ambassador.my_page.domain.service.AmbassadorStatusService;
import com.silicon2.admin.ambassador.my_page.domain.service.ReviewSubmissionService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class SubmitReviewUseCase {

    private final AmbassadorMemberRepository ambassadorMemberRepository;
    private final AmbassadorCampaignImageRepository campaignImageRepository;
    private final AmbassadorStatusService ambassadorStatusService;
    private final ReviewSubmissionService reviewSubmissionService;

    @Transactional
    public SubmitReviewResponse execute(Long memberId, SubmitReviewRequest request) {
        AmbassadorMember ambassador = ambassadorMemberRepository.findByMemberId(memberId)
            .orElseThrow(() -> new IllegalArgumentException("Ambassador not found"));

        ambassadorStatusService.validateAccess(ambassador);

        int existingImageCount = campaignImageRepository.countByAmbassadorMemberIdAndCampaignId(
            ambassador.getId(), request.getCampaignId());

        reviewSubmissionService.validateReviewSubmission(
            request.getCampaignId(),
            request.getCampaignStartDate(),
            request.getCampaignEndDate(),
            existingImageCount,
            request.getImageUrls().size()
        );

        List<AmbassadorCampaignImage> images = new ArrayList<>();
        for (int i = 0; i < request.getImageUrls().size(); i++) {
            images.add(AmbassadorCampaignImage.builder()
                .ambassadorMemberId(ambassador.getId())
                .campaignId(request.getCampaignId())
                .imageUrl(request.getImageUrls().get(i))
                .displayOrder(i + 1)
                .imageType("REVIEW")
                .createdAt(LocalDateTime.now())
                .build());
        }

        List<AmbassadorCampaignImage> savedImages = campaignImageRepository.saveAll(images);

        return SubmitReviewResponse.builder()
            .success(true)
            .reviewId(ambassador.getId())
            .imageCount(savedImages.size())
            .submittedAt(LocalDateTime.now())
            .build();
    }
}
