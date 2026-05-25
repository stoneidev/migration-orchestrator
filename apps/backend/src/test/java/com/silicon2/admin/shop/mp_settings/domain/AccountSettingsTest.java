package com.silicon2.admin.shop.mp_settings.domain;

import com.silicon2.admin.shop.mp_settings.domain.model.AccountSettings;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;

import static org.assertj.core.api.Assertions.assertThat;

class AccountSettingsTest {

    @Test
    @DisplayName("계정 설정 객체 생성 테스트")
    void createAccountSettings() {
        // given
        Long memberId = 1L;
        String email = "test@example.com";
        String name = "홍길동";

        // when
        AccountSettings accountSettings = AccountSettings.builder()
                .memberId(memberId)
                .email(email)
                .name(name)
                .phone("010-1234-5678")
                .emailNotificationEnabled(true)
                .smsNotificationEnabled(false)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        // then
        assertThat(accountSettings).isNotNull();
        assertThat(accountSettings.getMemberId()).isEqualTo(memberId);
        assertThat(accountSettings.getEmail()).isEqualTo(email);
        assertThat(accountSettings.getName()).isEqualTo(name);
    }

    @Test
    @DisplayName("비밀번호 변경 가능 여부 검증 - 성공")
    void canUpdatePassword_success() {
        // given
        AccountSettings accountSettings = AccountSettings.builder()
                .memberId(1L)
                .build();
        String currentPassword = "oldPassword123";
        String newPassword = "newPassword123";
        String confirmPassword = "newPassword123";

        // when
        boolean result = accountSettings.canUpdatePassword(currentPassword, newPassword, confirmPassword);

        // then
        assertThat(result).isTrue();
    }

    @Test
    @DisplayName("비밀번호 변경 가능 여부 검증 - 실패: 새 비밀번호 불일치")
    void canUpdatePassword_fail_mismatch() {
        // given
        AccountSettings accountSettings = AccountSettings.builder()
                .memberId(1L)
                .build();
        String currentPassword = "oldPassword123";
        String newPassword = "newPassword123";
        String confirmPassword = "differentPassword";

        // when
        boolean result = accountSettings.canUpdatePassword(currentPassword, newPassword, confirmPassword);

        // then
        assertThat(result).isFalse();
    }

    @Test
    @DisplayName("비밀번호 변경 가능 여부 검증 - 실패: 현재 비밀번호 없음")
    void canUpdatePassword_fail_noCurrentPassword() {
        // given
        AccountSettings accountSettings = AccountSettings.builder()
                .memberId(1L)
                .build();
        String newPassword = "newPassword123";
        String confirmPassword = "newPassword123";

        // when
        boolean result = accountSettings.canUpdatePassword(null, newPassword, confirmPassword);

        // then
        assertThat(result).isFalse();
    }

    @Test
    @DisplayName("계정 삭제 가능 여부 검증 - 성공")
    void canDeleteAccount_success() {
        // given
        AccountSettings accountSettings = AccountSettings.builder()
                .memberId(1L)
                .build();
        String password = "password123";

        // when
        boolean result = accountSettings.canDeleteAccount(password);

        // then
        assertThat(result).isTrue();
    }

    @Test
    @DisplayName("계정 삭제 가능 여부 검증 - 실패: 비밀번호 없음")
    void canDeleteAccount_fail_noPassword() {
        // given
        AccountSettings accountSettings = AccountSettings.builder()
                .memberId(1L)
                .build();

        // when
        boolean result = accountSettings.canDeleteAccount(null);

        // then
        assertThat(result).isFalse();
    }
}
