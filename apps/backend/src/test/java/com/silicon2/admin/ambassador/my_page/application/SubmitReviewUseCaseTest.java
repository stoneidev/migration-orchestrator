package com.silicon2.admin.ambassador.my_page.application;

import com.silicon2.admin.ambassador.my_page.application.dto.SubmitReviewRequest;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorStatus;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberRepository;
import com.silicon2.admin.testsupport.bdd.Bdd;
import com.silicon2.admin.testsupport.bdd.BddTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.BDDAssertions.thenCode;
import static org.assertj.core.api.BDDAssertions.thenThrownBy;
import static org.mockito.BDDMockito.given;

@BddTest
@DisplayName("SubmitReviewUseCase")
class SubmitReviewUseCaseTest {

    @Mock
    private AmbassadorMemberRepository ambassadorMemberRepository;

    @InjectMocks
    private SubmitReviewUseCase useCase;

    @Nested
    @DisplayName("리뷰 제출 시")
    class WhenSubmittingReview {

        @Test
        @DisplayName("활성 앰버서더는 리뷰를 제출할 수 있다")
        void shouldAllowActiveAmbassador() {
            SubmitReviewRequest request = SubmitReviewRequest.builder()
                    .memberId(100L)
                    .campaignId(1L)
                    .reviewContent("Great product!")
                    .imageUrls(List.of("url1", "url2"))
                    .build();

            Bdd.given(() -> given(ambassadorMemberRepository.findByMemberId(100L))
                    .willReturn(Optional.of(AmbassadorMember.builder()
                            .status(AmbassadorStatus.ACTIVE)
                            .build())));

            Bdd.then(() -> thenCode(() -> useCase.execute(request)).doesNotThrowAnyException());
        }

        @Test
        @DisplayName("비활성 앰버서더는 리뷰를 제출할 수 없다")
        void shouldRejectInactiveAmbassador() {
            SubmitReviewRequest request = SubmitReviewRequest.builder()
                    .memberId(100L)
                    .campaignId(1L)
                    .reviewContent("Great product!")
                    .build();

            Bdd.given(() -> given(ambassadorMemberRepository.findByMemberId(100L))
                    .willReturn(Optional.of(AmbassadorMember.builder()
                            .status(AmbassadorStatus.INACTIVE)
                            .build())));

            Bdd.then(() -> thenThrownBy(() -> useCase.execute(request))
                    .isInstanceOf(IllegalStateException.class)
                    .hasMessage("Only active ambassadors can submit reviews"));
        }

        @Test
        @DisplayName("이미지가 5개를 초과하면 예외를 발생시킨다")
        void shouldRejectTooManyImages() {
            SubmitReviewRequest request = SubmitReviewRequest.builder()
                    .memberId(100L)
                    .campaignId(1L)
                    .imageUrls(List.of("1", "2", "3", "4", "5", "6"))
                    .build();

            Bdd.then(() -> thenThrownBy(() -> useCase.execute(request))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessage("Maximum 5 images allowed"));
        }

        @Test
        @DisplayName("존재하지 않는 앰버서더이면 예외를 발생시킨다")
        void shouldThrowWhenAmbassadorNotFound() {
            SubmitReviewRequest request = SubmitReviewRequest.builder()
                    .memberId(999L)
                    .campaignId(1L)
                    .build();

            Bdd.given(() -> given(ambassadorMemberRepository.findByMemberId(999L))
                    .willReturn(Optional.empty()));

            Bdd.then(() -> thenThrownBy(() -> useCase.execute(request))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessage("Ambassador not found"));
        }
    }
}
