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
        AccountSettings accountSettings = accountSettingsRepository.findByMemberId(request.getMemberId())
                .orElseThrow(() -> new IllegalArgumentException("Member not found: " + request.getMemberId()));

        accountSettings.requireDeletion(request.getPassword());
        accountSettingsRepository.deleteByMemberId(request.getMemberId());
    }
}
