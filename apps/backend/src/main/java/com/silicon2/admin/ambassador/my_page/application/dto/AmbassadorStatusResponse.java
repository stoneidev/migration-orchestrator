package com.silicon2.admin.ambassador.my_page.application.dto;

import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AmbassadorStatusResponse {
    private Long memberId;
    private AmbassadorStatus status;
    private String trackingCode;
    private boolean canAccess;
}
