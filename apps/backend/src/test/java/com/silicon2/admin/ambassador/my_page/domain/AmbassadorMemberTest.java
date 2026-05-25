package com.silicon2.admin.ambassador.my_page.domain;

import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorMember;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorStatus;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;

import static org.assertj.core.api.Assertions.assertThat;

class AmbassadorMemberTest {

    @Test
    @DisplayName("ACTIVE 상태의 앰버서더는 활성 상태여야 한다")
    void activeAmbassadorShouldBeActive() {
        // given
        AmbassadorMember member = AmbassadorMember.builder()
                .id(1L)
                .memberId(100L)
                .status(AmbassadorStatus.ACTIVE)
                .trackingCode("AMB-001")
                .joinedAt(LocalDateTime.now())
                .build();

        // when
        boolean isActive = member.isActive();

        // then
        assertThat(isActive).isTrue();
    }

    @Test
    @DisplayName("INACTIVE 상태의 앰버서더는 비활성 상태여야 한다")
    void inactiveAmbassadorShouldNotBeActive() {
        // given
        AmbassadorMember member = AmbassadorMember.builder()
                .id(1L)
                .memberId(100L)
                .status(AmbassadorStatus.INACTIVE)
                .trackingCode("AMB-001")
                .joinedAt(LocalDateTime.now())
                .build();

        // when
        boolean isActive = member.isActive();

        // then
        assertThat(isActive).isFalse();
    }

    @Test
    @DisplayName("BANNED 상태의 앰버서더는 비활성 상태여야 한다")
    void bannedAmbassadorShouldNotBeActive() {
        // given
        AmbassadorMember member = AmbassadorMember.builder()
                .id(1L)
                .memberId(100L)
                .status(AmbassadorStatus.BANNED)
                .trackingCode("AMB-001")
                .joinedAt(LocalDateTime.now())
                .build();

        // when
        boolean isActive = member.isActive();

        // then
        assertThat(isActive).isFalse();
    }

    @Test
    @DisplayName("ACTIVE 상태의 앰버서더만 페이지에 접근할 수 있다")
    void onlyActiveAmbassadorCanAccessPage() {
        // given
        AmbassadorMember activeMember = AmbassadorMember.builder()
                .status(AmbassadorStatus.ACTIVE)
                .build();

        AmbassadorMember inactiveMember = AmbassadorMember.builder()
                .status(AmbassadorStatus.INACTIVE)
                .build();

        AmbassadorMember bannedMember = AmbassadorMember.builder()
                .status(AmbassadorStatus.BANNED)
                .build();

        // when & then
        assertThat(activeMember.canAccessPage()).isTrue();
        assertThat(inactiveMember.canAccessPage()).isFalse();
        assertThat(bannedMember.canAccessPage()).isFalse();
    }
}
