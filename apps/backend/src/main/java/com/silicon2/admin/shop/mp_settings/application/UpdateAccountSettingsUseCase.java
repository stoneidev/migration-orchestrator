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
        // BR001: User must be authenticated (delegated to controller/security)
        AccountSettings accountSettings = accountSettingsRepository.findByMemberId(request.getMemberId())
                .orElseThrow(() -> new IllegalArgumentException("Member not found: " + request.getMemberId()));

        // BR004: Email must be unique
        if (request.getEmail() != null && !request.getEmail().equals(accountSettings.getEmail())) {
            if (accountSettingsRepository.existsByEmail(request.getEmail())) {
                throw new IllegalArgumentException("Email already exists: " + request.getEmail());
            }
        }

        // BR002, BR003: Password change validation
        if (request.getCurrentPassword() != null) {
            if (!accountSettings.canUpdatePassword(
                    request.getCurrentPassword(),
                    request.getNewPassword(),
                    request.getConfirmPassword())) {
                throw new IllegalArgumentException("Invalid password change request");
            }
        }

        // BR006: XSS prevention (delegated to validation layer)
        AccountSettings updated = AccountSettings.builder()
                .memberId(accountSettings.getMemberId())
                .email(request.getEmail() != null ? request.getEmail() : accountSettings.getEmail())
                .name(request.getName() != null ? request.getName() : accountSettings.getName())
                .phone(request.getPhone() != null ? request.getPhone() : accountSettings.getPhone())
                .emailNotificationEnabled(
                        request.getEmailNotificationEnabled() != null ?
                                request.getEmailNotificationEnabled() :
                                accountSettings.isEmailNotificationEnabled())
                .smsNotificationEnabled(
                        request.getSmsNotificationEnabled() != null ?
                                request.getSmsNotificationEnabled() :
                                accountSettings.isSmsNotificationEnabled())
                .createdAt(accountSettings.getCreatedAt())
                .updatedAt(java.time.LocalDateTime.now())
                .build();

        accountSettingsRepository.save(updated);
    }
}
