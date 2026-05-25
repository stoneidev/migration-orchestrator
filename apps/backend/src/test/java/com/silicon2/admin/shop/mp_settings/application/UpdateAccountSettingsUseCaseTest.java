package com.silicon2.admin.shop.mp_settings.application;

import com.silicon2.admin.shop.mp_settings.application.dto.UpdateAccountSettingsRequest;
import com.silicon2.admin.shop.mp_settings.domain.model.AccountSettings;
import com.silicon2.admin.shop.mp_settings.domain.repository.AccountSettingsRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class UpdateAccountSettingsUseCaseTest {

    @Mock
    private AccountSettingsRepository accountSettingsRepository;

    @InjectMocks
    private UpdateAccountSettingsUseCase updateAccountSettingsUseCase;

    @Test
    @DisplayName("계정 설정 업데이트 성공")
    void execute_success() {
        // given
        Long memberId = 1L;
        AccountSettings existingSettings = AccountSettings.builder()
                .memberId(memberId)
                .email("old@example.com")
                .name("홍길동")
                .phone("010-1234-5678")
                .emailNotificationEnabled(true)
                .smsNotificationEnabled(false)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        UpdateAccountSettingsRequest request = UpdateAccountSettingsRequest.builder()
                .memberId(memberId)
                .email("new@example.com")
                .name("홍길동")
                .phone("010-9999-9999")
                .emailNotificationEnabled(false)
                .smsNotificationEnabled(true)
                .build();

        given(accountSettingsRepository.findByMemberId(memberId))
                .willReturn(Optional.of(existingSettings));
        given(accountSettingsRepository.existsByEmail("new@example.com"))
                .willReturn(false);

        // when
        updateAccountSettingsUseCase.execute(request);

        // then
        verify(accountSettingsRepository).save(any(AccountSettings.class));
    }

    @Test
    @DisplayName("계정 설정 업데이트 실패 - 이메일 중복")
    void execute_fail_emailAlreadyExists() {
        // given
        Long memberId = 1L;
        AccountSettings existingSettings = AccountSettings.builder()
                .memberId(memberId)
                .email("old@example.com")
                .name("홍길동")
                .phone("010-1234-5678")
                .emailNotificationEnabled(true)
                .smsNotificationEnabled(false)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        UpdateAccountSettingsRequest request = UpdateAccountSettingsRequest.builder()
                .memberId(memberId)
                .email("duplicate@example.com")
                .build();

        given(accountSettingsRepository.findByMemberId(memberId))
                .willReturn(Optional.of(existingSettings));
        given(accountSettingsRepository.existsByEmail("duplicate@example.com"))
                .willReturn(true);

        // when & then
        assertThatThrownBy(() -> updateAccountSettingsUseCase.execute(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Email already exists");
    }

    @Test
    @DisplayName("비밀번호 변경 실패 - 새 비밀번호 불일치")
    void execute_fail_passwordMismatch() {
        // given
        Long memberId = 1L;
        AccountSettings existingSettings = AccountSettings.builder()
                .memberId(memberId)
                .email("test@example.com")
                .name("홍길동")
                .phone("010-1234-5678")
                .emailNotificationEnabled(true)
                .smsNotificationEnabled(false)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        UpdateAccountSettingsRequest request = UpdateAccountSettingsRequest.builder()
                .memberId(memberId)
                .currentPassword("oldPassword")
                .newPassword("newPassword123")
                .confirmPassword("differentPassword")
                .build();

        given(accountSettingsRepository.findByMemberId(memberId))
                .willReturn(Optional.of(existingSettings));

        // when & then
        assertThatThrownBy(() -> updateAccountSettingsUseCase.execute(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Invalid password change request");
    }
}
