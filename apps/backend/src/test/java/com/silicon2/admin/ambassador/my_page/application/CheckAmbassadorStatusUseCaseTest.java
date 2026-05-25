package com.silicon2.admin.ambassador.my_page.application;

import com.silicon2.admin.ambassador.my_page.application.dto.AmbassadorStatusResponse;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorStatus;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.BDDMockito.given;

@ExtendWith(MockitoExtension.class)
class CheckAmbassadorStatusUseCaseTest {

    @Mock
    private AmbassadorMemberRepository ambassadorMemberRepository;

    @InjectMocks
    private CheckAmbassadorStatusUseCase useCase;

    @Test
    @DisplayName("활성 앰버서더의 상태를 성공적으로 조회한다")
    void shouldReturnActiveAmbassadorStatus() {
        // given
        Long memberId = 100L;
        AmbassadorMember member = AmbassadorMember.builder()
                .id(1L)
                .memberId(memberId)
                .status(AmbassadorStatus.ACTIVE)
                .trackingCode("AMB-001")
                .build();

        given(ambassadorMemberRepository.findByMemberId(memberId))
                .willReturn(Optional.of(member));

        // when
        AmbassadorStatusResponse response = useCase.execute(memberId);

        // then
        assertThat(response.getMemberId()).isEqualTo(memberId);
        assertThat(response.getStatus()).isEqualTo(AmbassadorStatus.ACTIVE);
        assertThat(response.getTrackingCode()).isEqualTo("AMB-001");
        assertThat(response.isCanAccess()).isTrue();
    }

    @Test
    @DisplayName("비활성 앰버서더는 접근 불가 상태를 반환한다")
    void shouldReturnInactiveAmbassadorCannotAccess() {
        // given
        Long memberId = 100L;
        AmbassadorMember member = AmbassadorMember.builder()
                .id(1L)
                .memberId(memberId)
                .status(AmbassadorStatus.INACTIVE)
                .trackingCode("AMB-002")
                .build();

        given(ambassadorMemberRepository.findByMemberId(memberId))
                .willReturn(Optional.of(member));

        // when
        AmbassadorStatusResponse response = useCase.execute(memberId);

        // then
        assertThat(response.getStatus()).isEqualTo(AmbassadorStatus.INACTIVE);
        assertThat(response.isCanAccess()).isFalse();
    }

    @Test
    @DisplayName("존재하지 않는 앰버서더 조회 시 예외를 발생시킨다")
    void shouldThrowExceptionWhenAmbassadorNotFound() {
        // given
        Long memberId = 999L;
        given(ambassadorMemberRepository.findByMemberId(memberId))
                .willReturn(Optional.empty());

        // when & then
        assertThatThrownBy(() -> useCase.execute(memberId))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("Ambassador not found");
    }
}
