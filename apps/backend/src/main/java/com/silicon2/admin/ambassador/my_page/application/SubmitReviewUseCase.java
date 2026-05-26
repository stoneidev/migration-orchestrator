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
        AmbassadorMember.validateReviewImageCount(request.getImageUrls());

        AmbassadorMember member = ambassadorMemberRepository.findByMemberId(request.getMemberId())
                .orElseThrow(() -> new IllegalArgumentException("Ambassador not found"));

        member.requireActiveForReview();
    }
}
