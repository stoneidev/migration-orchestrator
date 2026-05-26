package com.silicon2.admin.shop.mp_settings.domain.model;

import lombok.Builder;
import lombok.Getter;

import java.time.LocalDateTime;

@Getter
@Builder
public class AccountSettings {
    private Long memberId;
    private String email;
    private String name;
    private String phone;
    private boolean emailNotificationEnabled;
    private boolean smsNotificationEnabled;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public boolean canUpdatePassword(String currentPassword, String newPassword, String confirmPassword) {
        if (currentPassword == null || currentPassword.isEmpty()) {
            return false;
        }
        if (newPassword == null || newPassword.isEmpty()) {
            return false;
        }
        return newPassword.equals(confirmPassword);
    }

    public boolean canDeleteAccount(String passwordForVerification) {
        return passwordForVerification != null && !passwordForVerification.isEmpty();
    }

    public AccountSettings applyUpdate(
            String newEmail,
            String newName,
            String newPhone,
            Boolean newEmailNotificationEnabled,
            Boolean newSmsNotificationEnabled,
            String currentPassword,
            String newPassword,
            String confirmPassword,
            boolean emailAlreadyTaken
    ) {
        validateEmailChange(newEmail, emailAlreadyTaken);
        validatePasswordChange(currentPassword, newPassword, confirmPassword);

        return AccountSettings.builder()
                .memberId(memberId)
                .email(newEmail != null ? newEmail : email)
                .name(newName != null ? newName : name)
                .phone(newPhone != null ? newPhone : phone)
                .emailNotificationEnabled(
                        newEmailNotificationEnabled != null
                                ? newEmailNotificationEnabled
                                : emailNotificationEnabled)
                .smsNotificationEnabled(
                        newSmsNotificationEnabled != null
                                ? newSmsNotificationEnabled
                                : smsNotificationEnabled)
                .createdAt(createdAt)
                .updatedAt(LocalDateTime.now())
                .build();
    }

    public void requireDeletion(String password) {
        if (!canDeleteAccount(password)) {
            throw new IllegalArgumentException("Password verification failed");
        }
    }

    private void validateEmailChange(String newEmail, boolean emailAlreadyTaken) {
        if (newEmail != null && !newEmail.equals(email) && emailAlreadyTaken) {
            throw new IllegalArgumentException("Email already exists: " + newEmail);
        }
    }

    private void validatePasswordChange(String currentPassword, String newPassword, String confirmPassword) {
        if (currentPassword == null) {
            return;
        }
        if (!canUpdatePassword(currentPassword, newPassword, confirmPassword)) {
            throw new IllegalArgumentException("Invalid password change request");
        }
    }
}
