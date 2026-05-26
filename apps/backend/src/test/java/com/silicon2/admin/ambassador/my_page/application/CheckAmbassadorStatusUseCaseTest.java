package com.silicon2.admin.ambassador.my_page.application;

import com.silicon2.admin.ambassador.my_page.application.dto.AmbassadorStatusResponse;
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

import java.util.Optional;

import static org.assertj.core.api.BDDAssertions.then;
import static org.assertj.core.api.BDDAssertions.thenThrownBy;
import static org.mockito.BDDMockito.given;

@BddTest
@DisplayName("CheckAmbassadorStatusUseCase")
class CheckAmbassadorStatusUseCaseTest {

    @Mock
    private AmbassadorMemberRepository ambassadorMemberRepository;

    @InjectMocks
    private CheckAmbassadorStatusUseCase useCase;

    @Nested
    @DisplayName("앰버서더 상태 조회 시")
    class WhenCheckingStatus {

        @Test
        @DisplayName("활성 앰버서더의 상태와 접근 권한을 반환한다")
        void shouldReturnActiveAmbassadorStatus() {
            Long memberId = 100L;
            AmbassadorMember member = AmbassadorMember.builder()
                    .memberId(memberId)
                    .status(AmbassadorStatus.ACTIVE)
                    .trackingCode("AMB-001")
                    .build();

            Bdd.given(() -> given(ambassadorMemberRepository.findByMemberId(memberId))
                    .willReturn(Optional.of(member)));

            AmbassadorStatusResponse response = Bdd.when(() -> useCase.execute(memberId));

            Bdd.then(() -> {
                then(response.getStatus()).isEqualTo(AmbassadorStatus.ACTIVE);
                then(response.isCanAccess()).isTrue();
                then(response.getTrackingCode()).isEqualTo("AMB-001");
            });
        }

        @Test
        @DisplayName("비활성 앰버서더는 접근 불가 상태를 반환한다")
        void shouldReturnInactiveWithoutAccess() {
            Long memberId = 100L;
            AmbassadorMember member = AmbassadorMember.builder()
                    .memberId(memberId)
                    .status(AmbassadorStatus.INACTIVE)
                    .build();

            Bdd.given(() -> given(ambassadorMemberRepository.findByMemberId(memberId))
                    .willReturn(Optional.of(member)));

            AmbassadorStatusResponse response = Bdd.when(() -> useCase.execute(memberId));

            Bdd.then(() -> then(response.isCanAccess()).isFalse());
        }

        @Test
        @DisplayName("존재하지 않는 앰버서더이면 예외를 발생시킨다")
        void shouldThrowWhenAmbassadorNotFound() {
            Bdd.given(() -> given(ambassadorMemberRepository.findByMemberId(999L))
                    .willReturn(Optional.empty()));

            Bdd.then(() -> thenThrownBy(() -> useCase.execute(999L))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessage("Ambassador not found"));
        }
    }
}
