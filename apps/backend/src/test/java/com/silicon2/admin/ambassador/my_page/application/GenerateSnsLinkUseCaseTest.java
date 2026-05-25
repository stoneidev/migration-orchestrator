package com.silicon2.admin.ambassador.my_page.application;

import com.silicon2.admin.ambassador.my_page.application.dto.GenerateSnsLinkRequest;
import com.silicon2.admin.ambassador.my_page.application.dto.GenerateSnsLinkResponse;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMemberSns;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorStatus;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberRepository;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberSnsRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Collections;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.BDDMockito.given;

@ExtendWith(MockitoExtension.class)
class GenerateSnsLinkUseCaseTest {

    @Mock
    private AmbassadorMemberRepository ambassadorMemberRepository;

    @Mock
    private AmbassadorMemberSnsRepository ambassadorMemberSnsRepository;

    @InjectMocks
    private GenerateSnsLinkUseCase useCase;

    @Test
    @DisplayName("활성 앰버서더는 SNS 링크를 생성할 수 있다")
    void activeAmbassadorCanGenerateSnsLink() {
        // given
        Long memberId = 100L;
        AmbassadorMember member = AmbassadorMember.builder()
                .id(1L)
                .memberId(memberId)
                .status(AmbassadorStatus.ACTIVE)
                .trackingCode("AMB-001")
                .build();

        AmbassadorMemberSns sns = AmbassadorMemberSns.builder()
                .id(1L)
                .ambassadorMemberId(1L)
                .snsType("INSTAGRAM")
                .build();

        GenerateSnsLinkRequest request = GenerateSnsLinkRequest.builder()
                .memberId(memberId)
                .campaignId(10L)
                .snsType("INSTAGRAM")
                .build();

        given(ambassadorMemberRepository.findByMemberId(memberId))
                .willReturn(Optional.of(member));
        given(ambassadorMemberSnsRepository.findByAmbassadorMemberId(1L))
                .willReturn(List.of(sns));

        // when
        GenerateSnsLinkResponse response = useCase.execute(request);

        // then
        assertThat(response.getShareUrl()).contains("AMB-001");
        assertThat(response.getTrackingCode()).isEqualTo("AMB-001");
    }

    @Test
    @DisplayName("비활성 앰버서더는 SNS 링크를 생성할 수 없다")
    void inactiveAmbassadorCannotGenerateSnsLink() {
        // given
        Long memberId = 100L;
        AmbassadorMember member = AmbassadorMember.builder()
                .id(1L)
                .memberId(memberId)
                .status(AmbassadorStatus.INACTIVE)
                .build();

        GenerateSnsLinkRequest request = GenerateSnsLinkRequest.builder()
                .memberId(memberId)
                .campaignId(10L)
                .build();

        given(ambassadorMemberRepository.findByMemberId(memberId))
                .willReturn(Optional.of(member));

        // when & then
        assertThatThrownBy(() -> useCase.execute(request))
                .isInstanceOf(IllegalStateException.class)
                .hasMessage("Only active ambassadors can generate SNS links");
    }

    @Test
    @DisplayName("SNS 계정이 등록되지 않은 경우 링크 생성 불가")
    void cannotGenerateLinkWithoutSnsAccount() {
        // given
        Long memberId = 100L;
        AmbassadorMember member = AmbassadorMember.builder()
                .id(1L)
                .memberId(memberId)
                .status(AmbassadorStatus.ACTIVE)
                .trackingCode("AMB-001")
                .build();

        GenerateSnsLinkRequest request = GenerateSnsLinkRequest.builder()
                .memberId(memberId)
                .campaignId(10L)
                .build();

        given(ambassadorMemberRepository.findByMemberId(memberId))
                .willReturn(Optional.of(member));
        given(ambassadorMemberSnsRepository.findByAmbassadorMemberId(1L))
                .willReturn(Collections.emptyList());

        // when & then
        assertThatThrownBy(() -> useCase.execute(request))
                .isInstanceOf(IllegalStateException.class)
                .hasMessage("At least one SNS account must be registered");
    }

    @Test
    @DisplayName("존재하지 않는 앰버서더는 SNS 링크를 생성할 수 없다")
    void nonExistentAmbassadorCannotGenerateSnsLink() {
        // given
        Long memberId = 999L;
        GenerateSnsLinkRequest request = GenerateSnsLinkRequest.builder()
                .memberId(memberId)
                .campaignId(10L)
                .build();

        given(ambassadorMemberRepository.findByMemberId(memberId))
                .willReturn(Optional.empty());

        // when & then
        assertThatThrownBy(() -> useCase.execute(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessage("Ambassador not found");
    }
}
