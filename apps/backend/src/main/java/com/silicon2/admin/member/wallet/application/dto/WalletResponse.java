package com.silicon2.admin.member.wallet.application.dto;

import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class WalletResponse {
    private Boolean success;
    private WalletData data;
    private ErrorObject error;
}
