package com.silicon2.admin.member.wallet.application.dto;

import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MemberInfo {
    private String mbId;
    private Integer mbPoint;
    private String mbName;
    private String mbEmail;
}
