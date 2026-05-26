package com.silicon2.admin.shop.mp_settings.application;

import com.silicon2.admin.shop.mp_settings.application.dto.DeleteAccountRequest;
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
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

@BddTest
@DisplayName("DeleteAccountUseCase")
class DeleteAccountUseCaseTest {

    @Mock
    private AccountSettingsRepository accountSettingsRepository;

    @InjectMocks
    private DeleteAccountUseCase deleteAccountUseCase;

    @Nested
    @DisplayName("계정 삭제 시")
    class WhenDeletingAccount {

        @Test
        @DisplayName("비밀번호가 올바르면 계정을 삭제한다")
        void shouldDeleteAccountWhenPasswordValid() {
            Long memberId = 1L;
            DeleteAccountRequest request = DeleteAccountRequest.builder()
                    .memberId(memberId)
                    .password("correctPassword")
                    .build();

            Bdd.given(() -> given(accountSettingsRepository.findByMemberId(memberId))
                    .willReturn(Optional.of(accountSettings(memberId))));

            Bdd.when(() -> deleteAccountUseCase.execute(request));

            Bdd.then(() -> verify(accountSettingsRepository).deleteByMemberId(memberId));
        }

        @Test
        @DisplayName("비밀번호 검증에 실패하면 예외를 발생시킨다")
        void shouldRejectInvalidPassword() {
            DeleteAccountRequest request = DeleteAccountRequest.builder()
                    .memberId(1L)
                    .password(null)
                    .build();

            Bdd.given(() -> given(accountSettingsRepository.findByMemberId(1L))
                    .willReturn(Optional.of(accountSettings(1L))));

            Bdd.then(() -> thenThrownBy(() -> deleteAccountUseCase.execute(request))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("Password verification failed"));
        }

        @Test
        @DisplayName("존재하지 않는 회원이면 예외를 발생시킨다")
        void shouldThrowWhenMemberNotFound() {
            DeleteAccountRequest request = DeleteAccountRequest.builder()
                    .memberId(999L)
                    .password("password")
                    .build();

            Bdd.given(() -> given(accountSettingsRepository.findByMemberId(999L))
                    .willReturn(Optional.empty()));

            Bdd.then(() -> thenThrownBy(() -> deleteAccountUseCase.execute(request))
                    .isInstanceOf(IllegalArgumentException.class)
                    .hasMessageContaining("Member not found"));
        }
    }

    private AccountSettings accountSettings(Long memberId) {
        return AccountSettings.builder()
                .memberId(memberId)
                .email("test@example.com")
                .name("홍길동")
                .phone("010-1234-5678")
                .emailNotificationEnabled(true)
                .smsNotificationEnabled(false)
                .createdAt(LocalDateTime.now())
                .updatedAt(LocalDateTime.now())
                .build();
    }
}
