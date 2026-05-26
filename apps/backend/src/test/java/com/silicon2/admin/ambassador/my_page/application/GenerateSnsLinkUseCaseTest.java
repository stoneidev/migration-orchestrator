package com.silicon2.admin.ambassador.my_page.application;

import com.silicon2.admin.ambassador.my_page.application.dto.GenerateSnsLinkRequest;
import com.silicon2.admin.ambassador.my_page.application.dto.GenerateSnsLinkResponse;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMemberSns;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorStatus;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberRepository;
import com.silicon2.admin.ambassador.my_page.domain.repository.AmbassadorMemberSnsRepository;
import com.silicon2.admin.testsupport.bdd.Bdd;
import com.silicon2.admin.testsupport.bdd.BddTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;

import java.util.Collections;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.BDDAssertions.then;
import static org.assertj.core.api.BDDAssertions.thenThrownBy;
import static org.mockito.BDDMockito.given;

@BddTest
@DisplayName("GenerateSnsLinkUseCase")
class GenerateSnsLinkUseCaseTest {

    @Mock
    private AmbassadorMemberRepository ambassadorMemberRepository;

    @Mock
    private AmbassadorMemberSnsRepository ambassadorMemberSnsRepository;

    @InjectMocks
    private GenerateSnsLinkUseCase useCase;

    @Nested
    @DisplayName("SNS 링크 생성 시")
    class WhenGeneratingSnsLink {

        @Test
        @DisplayName("활성 앰버서더는 트래킹 코드가 포함된 링크를 생성한다")
        void shouldGenerateLinkForActiveAmbassador() {
            Long memberId = 100L;
            GenerateSnsLinkRequest request = GenerateSnsLinkRequest.builder()
                    .memberId(memberId)
                    .campaignId(10L)
                    .build();

            AmbassadorMember member = AmbassadorMember.builder()
                    .id(1L)
                    .memberId(memberId)
                    .status(AmbassadorStatus.ACTIVE)
                    .trackingCode("AMB-001")
                    .build();

            Bdd.given(() -> {
                given(ambassadorMemberRepository.findByMemberId(memberId))
                        .willReturn(Optional.of(member));
                given(ambassadorMemberSnsRepository.findByAmbassadorMemberId(1L))
                        .willReturn(List.of(AmbassadorMemberSns.builder().id(1L).build()));
            });

            GenerateSnsLinkResponse response = Bdd.when(() -> useCase.execute(request));

            Bdd.then(() -> {
                then(response.getShareUrl()).contains("AMB-001");
                then(response.getTrackingCode()).isEqualTo("AMB-001");
            });
        }

        @Test
        @DisplayName("비활성 앰버서더는 링크를 생성할 수 없다")
        void shouldRejectInactiveAmbassador() {
            GenerateSnsLinkRequest request = GenerateSnsLinkRequest.builder()
                    .memberId(100L)
                    .campaignId(10L)
                    .build();

            Bdd.given(() -> given(ambassadorMemberRepository.findByMemberId(100L))
                    .willReturn(Optional.of(AmbassadorMember.builder()
                            .status(AmbassadorStatus.INACTIVE)
                            .build())));

            Bdd.then(() -> thenThrownBy(() -> useCase.execute(request))
                    .isInstanceOf(IllegalStateException.class)
                    .hasMessage("Only active ambassadors can generate SNS links"));
        }

        @Test
        @DisplayName("SNS 계정이 없으면 링크를 생성할 수 없다")
        void shouldRejectWithoutSnsAccount() {
            GenerateSnsLinkRequest request = GenerateSnsLinkRequest.builder()
                    .memberId(100L)
                    .campaignId(10L)
                    .build();

            Bdd.given(() -> {
                given(ambassadorMemberRepository.findByMemberId(100L))
                        .willReturn(Optional.of(AmbassadorMember.builder()
                                .id(1L)
                                .status(AmbassadorStatus.ACTIVE)
                                .build()));
                given(ambassadorMemberSnsRepository.findByAmbassadorMemberId(1L))
                        .willReturn(Collections.emptyList());
            });

            Bdd.then(() -> thenThrownBy(() -> useCase.execute(request))
                    .isInstanceOf(IllegalStateException.class)
                    .hasMessage("At least one SNS account must be registered"));
        }

        @Test
        @DisplayName("존재하지 않는 앰버서더이면 예외를 발생시킨다")
        void shouldThrowWhenAmbassadorNotFound() {
            GenerateSnsLinkRequest request = GenerateSnsLinkRequest.builder()
                    .memberId(999L)
                    .campaignId(10L)
                    .build();

            Bdd.given(() -> given(ambassadorMemberRepository.findByMemberId(999L))
                    .willReturn(Optional.empty()));

            Bdd.then(() -> thenThrownBy(() -> useCase.execute(request))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessage("Ambassador not found"));
        }
    }
}
