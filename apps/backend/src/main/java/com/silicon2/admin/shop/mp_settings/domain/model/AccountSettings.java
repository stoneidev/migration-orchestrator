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
}
