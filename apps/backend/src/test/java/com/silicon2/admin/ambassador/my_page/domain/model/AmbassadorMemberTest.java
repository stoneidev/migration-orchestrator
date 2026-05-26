package com.silicon2.admin.ambassador.my_page.domain.model;

import com.silicon2.admin.testsupport.bdd.Bdd;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.List;

import static org.assertj.core.api.BDDAssertions.then;
import static org.assertj.core.api.BDDAssertions.thenCode;
import static org.assertj.core.api.BDDAssertions.thenThrownBy;

@DisplayName("AmbassadorMember")
class AmbassadorMemberTest {

    @Nested
    @DisplayName("활성 상태 확인 시")
    class WhenCheckingActiveStatus {

        @Test
        @DisplayName("ACTIVE 상태이면 활성으로 판단한다")
        void shouldBeActiveWhenStatusIsActive() {
            AmbassadorMember member = memberWithStatus(AmbassadorStatus.ACTIVE);

            boolean isActive = Bdd.when(member::isActive);

            Bdd.then(() -> then(isActive).isTrue());
        }

        @Test
        @DisplayName("INACTIVE 또는 BANNED 상태이면 비활성으로 판단한다")
        void shouldBeInactiveWhenNotActive() {
            AmbassadorMember inactive = memberWithStatus(AmbassadorStatus.INACTIVE);
            AmbassadorMember banned = memberWithStatus(AmbassadorStatus.BANNED);

            Bdd.then(() -> {
                then(inactive.isActive()).isFalse();
                then(banned.isActive()).isFalse();
            });
        }
    }

    @Nested
    @DisplayName("페이지 접근 권한 확인 시")
    class WhenCheckingPageAccess {

        @Test
        @DisplayName("ACTIVE 상태만 페이지 접근이 가능하다")
        void shouldAllowAccessOnlyForActive() {
            AmbassadorMember active = memberWithStatus(AmbassadorStatus.ACTIVE);
            AmbassadorMember inactive = memberWithStatus(AmbassadorStatus.INACTIVE);

            Bdd.then(() -> {
                then(active.canAccessPage()).isTrue();
                then(inactive.canAccessPage()).isFalse();
            });
        }
    }

    @Nested
    @DisplayName("SNS 링크 생성 시")
    class WhenGeneratingSnsLink {

        @Test
        @DisplayName("활성 앰버서더만 SNS 링크를 생성할 수 있다")
        void shouldRequireActiveStatus() {
            AmbassadorMember active = memberWithStatus(AmbassadorStatus.ACTIVE);
            AmbassadorMember inactive = memberWithStatus(AmbassadorStatus.INACTIVE);

            Bdd.then(() -> {
                thenCode(active::requireActiveForSnsLink).doesNotThrowAnyException();
                thenThrownBy(inactive::requireActiveForSnsLink)
                        .isInstanceOf(IllegalStateException.class);
            });
        }

        @Test
        @DisplayName("캠페인 링크에 트래킹 코드가 포함된다")
        void shouldIncludeTrackingCodeInLink() {
            AmbassadorMember member = AmbassadorMember.builder()
                    .trackingCode("AMB-001")
                    .build();

            String link = Bdd.when(() -> member.generateCampaignLink(10L));

            Bdd.then(() -> then(link).isEqualTo("https://example.com/campaign/10?ref=AMB-001"));
        }
    }

    @Nested
    @DisplayName("리뷰 제출 시")
    class WhenSubmittingReview {

        @Test
        @DisplayName("이미지는 최대 5개까지만 허용된다")
        void shouldLimitImageCountToFive() {
            Bdd.then(() -> {
                thenCode(() -> AmbassadorMember.validateReviewImageCount(List.of("a", "b")))
                        .doesNotThrowAnyException();
                thenThrownBy(() -> AmbassadorMember.validateReviewImageCount(
                        List.of("1", "2", "3", "4", "5", "6")))
                        .isInstanceOf(IllegalArgumentException.class)
                        .hasMessage("Maximum 5 images allowed");
            });
        }

        @Test
        @DisplayName("활성 앰버서더만 리뷰를 제출할 수 있다")
        void shouldRequireActiveForReview() {
            AmbassadorMember inactive = memberWithStatus(AmbassadorStatus.INACTIVE);

            Bdd.then(() -> thenThrownBy(inactive::requireActiveForReview)
                    .isInstanceOf(IllegalStateException.class));
        }
    }

    private AmbassadorMember memberWithStatus(AmbassadorStatus status) {
        return AmbassadorMember.builder()
                .id(1L)
                .memberId(100L)
                .status(status)
                .trackingCode("AMB-001")
                .joinedAt(LocalDateTime.now())
                .build();
    }
}
