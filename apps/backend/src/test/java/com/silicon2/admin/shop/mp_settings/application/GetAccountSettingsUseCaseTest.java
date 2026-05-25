package com.silicon2.admin.shop.mp_settings.application;

import com.silicon2.admin.shop.mp_settings.application.dto.AccountSettingsResponse;
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

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.BDDMockito.given;

@ExtendWith(MockitoExtension.class)
class GetAccountSettingsUseCaseTest {

    @Mock
    private AccountSettingsRepository accountSettingsRepository;

    @InjectMocks
    private GetAccountSettingsUseCase getAccountSettingsUseCase;

    @Test
    @DisplayName("계정 설정 조회 성공")
    void execute_success() {
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

        given(accountSettingsRepository.findByMemberId(memberId))
                .willReturn(Optional.of(accountSettings));

        // when
        AccountSettingsResponse response = getAccountSettingsUseCase.execute(memberId);

        // then
        assertThat(response).isNotNull();
        assertThat(response.getMemberId()).isEqualTo(memberId);
        assertThat(response.getEmail()).isEqualTo("test@example.com");
        assertThat(response.getName()).isEqualTo("홍길동");
        assertThat(response.getPhone()).isEqualTo("010-1234-5678");
        assertThat(response.isEmailNotificationEnabled()).isTrue();
        assertThat(response.isSmsNotificationEnabled()).isFalse();
    }

    @Test
    @DisplayName("계정 설정 조회 실패 - 회원 없음")
    void execute_fail_memberNotFound() {
        // given
        Long memberId = 999L;
        given(accountSettingsRepository.findByMemberId(memberId))
                .willReturn(Optional.empty());

        // when & then
        assertThatThrownBy(() -> getAccountSettingsUseCase.execute(memberId))
                .isInstanceOf(IllegalArgumentException.class)
                .hasMessageContaining("Member not found");
    }
}
