package com.silicon2.admin.shop.mp_settings.application;

import com.silicon2.admin.shop.mp_settings.application.dto.UpdateAccountSettingsRequest;
import com.silicon2.admin.shop.mp_settings.domain.model.AccountSettings;
import com.silicon2.admin.shop.mp_settings.domain.repository.AccountSettingsRepository;
import com.silicon2.admin.testsupport.bdd.Bdd;
import com.silicon2.admin.testsupport.bdd.BddTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;

import java.time.LocalDateTime;
import java.util.Optional;

import static org.assertj.core.api.BDDAssertions.thenThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

@BddTest
@DisplayName("UpdateAccountSettingsUseCase")
class UpdateAccountSettingsUseCaseTest {

    @Mock
    private AccountSettingsRepository accountSettingsRepository;

    @InjectMocks
    private UpdateAccountSettingsUseCase updateAccountSettingsUseCase;

    @Nested
    @DisplayName("계정 설정 업데이트 시")
    class WhenUpdatingSettings {

        @Test
        @DisplayName("유효한 요청이면 설정을 저장한다")
        void shouldSaveUpdatedSettings() {
            Long memberId = 1L;
            AccountSettings existing = existingSettings(memberId);

            UpdateAccountSettingsRequest request = UpdateAccountSettingsRequest.builder()
                    .memberId(memberId)
                    .email("new@example.com")
                    .phone("010-9999-9999")
                    .build();

            Bdd.given(() -> {
                given(accountSettingsRepository.findByMemberId(memberId))
                        .willReturn(Optional.of(existing));
                given(accountSettingsRepository.existsByEmail("new@example.com"))
                        .willReturn(false);
            });

            Bdd.when(() -> updateAccountSettingsUseCase.execute(request));

            Bdd.then(() -> verify(accountSettingsRepository).save(any(AccountSettings.class)));
        }

        @Test
        @DisplayName("이메일이 중복이면 예외를 발생시킨다")
        void shouldRejectDuplicateEmail() {
            Long memberId = 1L;
            UpdateAccountSettingsRequest request = UpdateAccountSettingsRequest.builder()
                    .memberId(memberId)
                    .email("duplicate@example.com")
                    .build();

            Bdd.given(() -> {
                given(accountSettingsRepository.findByMemberId(memberId))
                        .willReturn(Optional.of(existingSettings(memberId)));
                given(accountSettingsRepository.existsByEmail("duplicate@example.com"))
                        .willReturn(true);
            });

            Bdd.then(() -> thenThrownBy(() -> updateAccountSettingsUseCase.execute(request))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("Email already exists"));
        }

        @Test
        @DisplayName("비밀번호 확인이 일치하지 않으면 예외를 발생시킨다")
        void shouldRejectPasswordMismatch() {
            Long memberId = 1L;
            UpdateAccountSettingsRequest request = UpdateAccountSettingsRequest.builder()
                    .memberId(memberId)
                    .currentPassword("oldPassword")
                    .newPassword("newPassword123")
                    .confirmPassword("differentPassword")
                    .build();

            Bdd.given(() -> given(accountSettingsRepository.findByMemberId(memberId))
                    .willReturn(Optional.of(existingSettings(memberId))));

            Bdd.then(() -> thenThrownBy(() -> updateAccountSettingsUseCase.execute(request))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("Invalid password change request"));
        }
    }

    private AccountSettings existingSettings(Long memberId) {
        return AccountSettings.builder()
                .memberId(memberId)
                .email("old@example.com")
                .name("홍길동")
                .phone("010-1234-5678")
                .emailNotificationEnabled(true)
                .smsNotificationEnabled(false)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();
    }
}
