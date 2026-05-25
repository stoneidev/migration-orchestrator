package com.silicon2.admin.member.wallet.application.dto;

import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ErrorObject {
    private String code;
    private String message;
    private Object details;
}
