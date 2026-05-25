package com.silicon2.admin.ambassador.my_page.application;

import com.silicon2.admin.ambassador.my_page.application.dto.SubmitReviewRequest;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional
public class SubmitReviewUseCase {

    private final AmbassadorMemberRepository ambassadorMemberRepository;

    public void execute(SubmitReviewRequest request) {
        // BR-007: Maximum of 5 images allowed per review submission
        if (request.getImageUrls() != null && request.getImageUrls().size() > 5) {
            throw new IllegalArgumentException("Maximum 5 images allowed");
        }

        AmbassadorMember member = ambassadorMemberRepository.findByMemberId(request.getMemberId())
                .orElseThrow(() -> new IllegalArgumentException("Ambassador not found"));

        // BR-001: Only active ambassadors can submit reviews
        if (!member.isActive()) {
            throw new IllegalStateException("Only active ambassadors can submit reviews");
        }

        // BR-003: Each ambassador may submit only one review per campaign
        // Note: This will be fully implemented with campaign repository in Layer 5
    }
}
