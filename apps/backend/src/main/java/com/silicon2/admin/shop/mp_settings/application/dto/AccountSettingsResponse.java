package com.silicon2.admin.shop.mp_settings.application.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AccountSettingsResponse {
    private Long memberId;
    private String email;
    private String name;
    private String phone;
    private boolean emailNotificationEnabled;
    private boolean smsNotificationEnabled;
}
