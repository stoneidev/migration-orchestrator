package com.silicon2.admin.ambassador.my_page.application;

import com.silicon2.admin.ambassador.my_page.application.dto.SubmitReviewRequest;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorStatus;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Arrays;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThatCode;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.BDDMockito.given;

@ExtendWith(MockitoExtension.class)
class SubmitReviewUseCaseTest {

    @Mock
    private AmbassadorMemberRepository ambassadorMemberRepository;

    @InjectMocks
    private SubmitReviewUseCase useCase;

    @Test
    @DisplayName("활성 앰버서더는 리뷰를 제출할 수 있다")
    void activeAmbassadorCanSubmitReview() {
        // given
        Long memberId = 100L;
        AmbassadorMember member = AmbassadorMember.builder()
                .id(1L)
                .memberId(memberId)
                .status(AmbassadorStatus.ACTIVE)
                .build();

        SubmitReviewRequest request = SubmitReviewRequest.builder()
                .memberId(memberId)
                .campaignId(1L)
                .reviewContent("Great product!")
                .imageUrls(Arrays.asList("url1", "url2"))
                .build();

        given(ambassadorMemberRepository.findByMemberId(memberId))
                .willReturn(Optional.of(member));

        // when & then
        assertThatCode(() -> useCase.execute(request))
                .doesNotThrowAnyException();
    }

    @Test
    @DisplayName("비활성 앰버서더는 리뷰를 제출할 수 없다")
    void inactiveAmbassadorCannotSubmitReview() {
        // given
        Long memberId = 100L;
        AmbassadorMember member = AmbassadorMember.builder()
                .id(1L)
                .memberId(memberId)
                .status(AmbassadorStatus.INACTIVE)
                .build();

        SubmitReviewRequest request = SubmitReviewRequest.builder()
                .memberId(memberId)
                .campaignId(1L)
                .reviewContent("Great product!")
                .build();

        given(ambassadorMemberRepository.findByMemberId(memberId))
                .willReturn(Optional.of(member));

        // when & then
        assertThatThrownBy(() -> useCase.execute(request))
                .isInstanceOf(IllegalStateException.class)
                .hasMessage("Only active ambassadors can submit reviews");
    }

    @Test
    @DisplayName("이미지는 최대 5개까지만 제출할 수 있다")
    void shouldNotAllowMoreThan5Images() {
        // given
        SubmitReviewRequest request = SubmitReviewRequest.builder()
                .memberId(100L)
                .campaignId(1L)
                .reviewContent("Great product!")
                .imageUrls(Arrays.asList("url1", "url2", "url3", "url4", "url5", "url6"))
                .build();

        // when & then
        assertThatThrownBy(() -> useCase.execute(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("Maximum 5 images allowed");
    }

    @Test
    @DisplayName("존재하지 않는 앰버서더는 리뷰를 제출할 수 없다")
    void nonExistentAmbassadorCannotSubmitReview() {
        // given
        Long memberId = 999L;
        SubmitReviewRequest request = SubmitReviewRequest.builder()
                .memberId(memberId)
                .campaignId(1L)
                .reviewContent("Great product!")
                .build();

        given(ambassadorMemberRepository.findByMemberId(memberId))
                .willReturn(Optional.empty());

        // when & then
        assertThatThrownBy(() -> useCase.execute(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("Ambassador not found");
    }
}
