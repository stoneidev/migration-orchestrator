package com.silicon2.admin.shop.mp_settings.application;

import com.silicon2.admin.shop.mp_settings.application.dto.AccountSettingsResponse;
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

import static org.assertj.core.api.BDDAssertions.then;
import static org.assertj.core.api.BDDAssertions.thenThrownBy;
import static org.mockito.BDDMockito.given;

@BddTest
@DisplayName("GetAccountSettingsUseCase")
class GetAccountSettingsUseCaseTest {

    @Mock
    private AccountSettingsRepository accountSettingsRepository;

    @InjectMocks
    private GetAccountSettingsUseCase getAccountSettingsUseCase;

    @Nested
    @DisplayName("계정 설정 조회 시")
    class WhenGettingSettings {

        @Test
        @DisplayName("존재하는 회원의 설정을 반환한다")
        void shouldReturnAccountSettings() {
            Long memberId = 1L;
            AccountSettings settings = accountSettings(memberId);

            Bdd.given(() -> given(accountSettingsRepository.findByMemberId(memberId))
                    .willReturn(Optional.of(settings)));

            AccountSettingsResponse response = Bdd.when(() -> getAccountSettingsUseCase.execute(memberId));

            Bdd.then(() -> {
                then(response.getMemberId()).isEqualTo(memberId);
                then(response.getEmail()).isEqualTo("test@example.com");
                then(response.getName()).isEqualTo("홍길동");
                then(response.isEmailNotificationEnabled()).isTrue();
            });
        }

        @Test
        @DisplayName("존재하지 않는 회원이면 예외를 발생시킨다")
        void shouldThrowWhenMemberNotFound() {
            Bdd.given(() -> given(accountSettingsRepository.findByMemberId(999L))
                    .willReturn(Optional.empty()));

            Bdd.then(() -> thenThrownBy(() -> getAccountSettingsUseCase.execute(999L))
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
