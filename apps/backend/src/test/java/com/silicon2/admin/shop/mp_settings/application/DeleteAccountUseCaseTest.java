package com.silicon2.admin.shop.mp_settings.application;

import com.silicon2.admin.shop.mp_settings.application.dto.DeleteAccountRequest;
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
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class DeleteAccountUseCaseTest {

    @Mock
    private AccountSettingsRepository accountSettingsRepository;

    @InjectMocks
    private DeleteAccountUseCase deleteAccountUseCase;

    @Test
    @DisplayName("계정 삭제 성공")
    void execute_success() {
        // given
        Long memberId = 1L;
        String password = "correctPassword";

        AccountSettings accountSettings = AccountSettings.builder()
                .memberId(memberId)
                .email("test@example.com")
                .name("홍길동")
                .phone("010-1234-5678")
                .emailNotificationEnabled(true)
                .smsNotificationEnabled(false)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        DeleteAccountRequest request = DeleteAccountRequest.builder()
                .memberId(memberId)
                .password(password)
                .build();

        given(accountSettingsRepository.findByMemberId(memberId))
                .willReturn(Optional.of(accountSettings));

        // when
        deleteAccountUseCase.execute(request);

        // then
        verify(accountSettingsRepository).deleteByMemberId(memberId);
    }

    @Test
    @DisplayName("계정 삭제 실패 - 비밀번호 검증 실패")
    void execute_fail_invalidPassword() {
        // given
        Long memberId = 1L;
        AccountSettings accountSettings = AccountSettings.builder()
                .memberId(memberId)
                .email("test@example.com")
                .name("홍길동")
                .phone("010-1234-5678")
                .emailNotificationEnabled(true)
                .smsNotificationEnabled(false)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();

        DeleteAccountRequest request = DeleteAccountRequest.builder()
                .memberId(memberId)
                .password(null)
                .build();

        given(accountSettingsRepository.findByMemberId(memberId))
                .willReturn(Optional.of(accountSettings));

        // when & then
        assertThatThrownBy(() -> deleteAccountUseCase.execute(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Password verification failed");
    }

    @Test
    @DisplayName("계정 삭제 실패 - 회원 없음")
    void execute_fail_memberNotFound() {
        // given
        Long memberId = 999L;
        DeleteAccountRequest request = DeleteAccountRequest.builder()
                .memberId(memberId)
                .password("password")
                .build();

        given(accountSettingsRepository.findByMemberId(memberId))
                .willReturn(Optional.empty());

        // when & then
        assertThatThrownBy(() -> deleteAccountUseCase.execute(request))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Member not found");
    }
}
