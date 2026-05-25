package com.silicon2.admin.shop.mp_settings.application;

import com.silicon2.admin.shop.mp_settings.application.dto.DeleteAccountRequest;
import com.silicon2.admin.shop.mp_settings.domain.model.AccountSettings;
import com.silicon2.admin.shop.mp_settings.domain.repository.AccountSettingsRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional
public class DeleteAccountUseCase {

    private final AccountSettingsRepository accountSettingsRepository;

    public void execute(DeleteAccountRequest request) {
        // BR001: User must be authenticated (delegated to controller/security)
        AccountSettings accountSettings = accountSettingsRepository.findByMemberId(request.getMemberId())
                .orElseThrow(() -> new IllegalArgumentException("Member not found: " + request.getMemberId()));

        // BR005: Password verification required
        if (!accountSettings.canDeleteAccount(request.getPassword())) {
            throw new IllegalArgumentException("Password verification failed");
        }

        // BR008: Process expired points (delegated to event handler or separate service)
        // BR007: Recalculate member points (delegated to event handler)

        accountSettingsRepository.deleteByMemberId(request.getMemberId());
    }
}
