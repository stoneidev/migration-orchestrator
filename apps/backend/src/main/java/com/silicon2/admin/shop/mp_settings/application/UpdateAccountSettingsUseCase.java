package com.silicon2.admin.shop.mp_settings.application;

import com.silicon2.admin.shop.mp_settings.application.dto.UpdateAccountSettingsRequest;
import com.silicon2.admin.shop.mp_settings.domain.model.AccountSettings;
import com.silicon2.admin.shop.mp_settings.domain.repository.AccountSettingsRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
@Transactional
public class UpdateAccountSettingsUseCase {

    private final AccountSettingsRepository accountSettingsRepository;

    public void execute(UpdateAccountSettingsRequest request) {
        AccountSettings accountSettings = accountSettingsRepository.findByMemberId(request.getMemberId())
                .orElseThrow(() -> new IllegalArgumentException("Member not found: " + request.getMemberId()));

        boolean emailAlreadyTaken = request.getEmail() != null
                && !request.getEmail().equals(accountSettings.getEmail())
                && accountSettingsRepository.existsByEmail(request.getEmail());

        AccountSettings updated = accountSettings.applyUpdate(
                request.getEmail(),
                request.getName(),
                request.getPhone(),
                request.getEmailNotificationEnabled(),
                request.getSmsNotificationEnabled(),
                request.getCurrentPassword(),
                request.getNewPassword(),
                request.getConfirmPassword(),
                emailAlreadyTaken
        );

        accountSettingsRepository.save(updated);
    }
}
