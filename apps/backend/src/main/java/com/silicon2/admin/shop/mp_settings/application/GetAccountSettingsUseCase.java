package com.silicon2.admin.shop.mp_settings.application;

import com.silicon2.admin.shop.mp_settings.application.dto.AccountSettingsResponse;
import com.silicon2.admin.shop.mp_settings.domain.model.AccountSettings;
import com.silicon2.admin.shop.mp_settings.domain.repository.AccountSettingsRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class GetAccountSettingsUseCase {

    private final AccountSettingsRepository accountSettingsRepository;

    public AccountSettingsResponse execute(Long memberId) {
        AccountSettings accountSettings = accountSettingsRepository.findByMemberId(memberId)
                .orElseThrow(() -> new IllegalArgumentException("Member not found: " + memberId));

        return AccountSettingsResponse.builder()
                .memberId(accountSettings.getMemberId())
                .email(accountSettings.getEmail())
                .name(accountSettings.getName())
                .phone(accountSettings.getPhone())
                .emailNotificationEnabled(accountSettings.isEmailNotificationEnabled())
                .smsNotificationEnabled(accountSettings.isSmsNotificationEnabled())
                .build();
    }
}
