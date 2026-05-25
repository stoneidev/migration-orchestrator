package com.silicon2.admin.shop.mp_settings.application.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DeleteAccountRequest {
    private Long memberId;
    private String password;
}
