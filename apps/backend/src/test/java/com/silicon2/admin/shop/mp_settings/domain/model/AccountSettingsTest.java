package com.silicon2.admin.shop.mp_settings.domain.model;

import com.silicon2.admin.testsupport.bdd.Bdd;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;

import static org.assertj.core.api.BDDAssertions.then;
import static org.assertj.core.api.BDDAssertions.thenThrownBy;

@DisplayName("AccountSettings")
class AccountSettingsTest {

    @Nested
    @DisplayName("비밀번호 변경 검증 시")
    class WhenValidatingPasswordChange {

        @Test
        @DisplayName("현재·새·확인 비밀번호가 일치하면 변경 가능하다")
        void shouldAllowPasswordChangeWhenValid() {
            AccountSettings settings = settingsWithMemberId(1L);

            boolean result = Bdd.when(() -> settings.canUpdatePassword(
                    "oldPassword123", "newPassword123", "newPassword123"
            ));

            Bdd.then(() -> then(result).isTrue());
        }

        @Test
        @DisplayName("새 비밀번호와 확인 비밀번호가 다르면 변경 불가하다")
        void shouldRejectMismatchedPasswords() {
            AccountSettings settings = settingsWithMemberId(1L);

            boolean result = Bdd.when(() -> settings.canUpdatePassword(
                    "oldPassword123", "newPassword123", "differentPassword"
            ));

            Bdd.then(() -> then(result).isFalse());
        }

        @Test
        @DisplayName("현재 비밀번호가 없으면 변경 불가하다")
        void shouldRejectMissingCurrentPassword() {
            AccountSettings settings = settingsWithMemberId(1L);

            boolean result = Bdd.when(() -> settings.canUpdatePassword(
                    null, "newPassword123", "newPassword123"
            ));

            Bdd.then(() -> then(result).isFalse());
        }
    }

    @Nested
    @DisplayName("계정 삭제 검증 시")
    class WhenValidatingDeletion {

        @Test
        @DisplayName("비밀번호가 있으면 삭제 가능하다")
        void shouldAllowDeletionWithPassword() {
            AccountSettings settings = settingsWithMemberId(1L);

            boolean result = Bdd.when(() -> settings.canDeleteAccount("password123"));

            Bdd.then(() -> then(result).isTrue());
        }

        @Test
        @DisplayName("비밀번호가 없으면 삭제 불가하다")
        void shouldRejectDeletionWithoutPassword() {
            AccountSettings settings = settingsWithMemberId(1L);

            Bdd.then(() -> thenThrownBy(() -> settings.requireDeletion(null))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessage("Password verification failed"));
        }
    }

    @Nested
    @DisplayName("설정 업데이트 시")
    class WhenApplyingUpdate {

        @Test
        @DisplayName("변경된 필드만 병합하여 새 객체를 반환한다")
        void shouldMergeUpdatedFields() {
            AccountSettings existing = AccountSettings.builder()
                    .memberId(1L)
                    .email("old@example.com")
                    .name("홍길동")
                    .phone("010-1234-5678")
                    .emailNotificationEnabled(true)
                    .smsNotificationEnabled(false)
                    .createdAt(LocalDateTime.now())
                    .updatedAt(LocalDateTime.now())
                    .build();

            AccountSettings updated = Bdd.when(() -> existing.applyUpdate(
                    "new@example.com", null, "010-9999-9999",
                    false, true, null, null, null, false
            ));

            Bdd.then(() -> {
                then(updated.getEmail()).isEqualTo("new@example.com");
                then(updated.getName()).isEqualTo("홍길동");
                then(updated.getPhone()).isEqualTo("010-9999-9999");
                then(updated.isSmsNotificationEnabled()).isTrue();
            });
        }

        @Test
        @DisplayName("이메일이 중복이면 예외를 발생시킨다")
        void shouldRejectDuplicateEmail() {
            AccountSettings existing = AccountSettings.builder()
                    .memberId(1L)
                    .email("old@example.com")
                    .build();

            Bdd.then(() -> thenThrownBy(() -> existing.applyUpdate(
                    "duplicate@example.com", null, null, null, null,
                    null, null, null, true
            ))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("Email already exists"));
        }
    }

    private AccountSettings settingsWithMemberId(Long memberId) {
        return AccountSettings.builder().memberId(memberId).build();
    }
}
