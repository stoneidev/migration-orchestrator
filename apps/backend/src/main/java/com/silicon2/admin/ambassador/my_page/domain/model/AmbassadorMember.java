package com.silicon2.admin.ambassador.my_page.domain.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AmbassadorMember {
    private Long id;
    private Long memberId;
    private AmbassadorStatus status;
    private String trackingCode;
    private LocalDateTime joinedAt;
    private LocalDateTime updatedAt;

    public boolean isActive() {
        return status == AmbassadorStatus.ACTIVE;
    }

    public boolean canAccessPage() {
        return status == AmbassadorStatus.ACTIVE;
    }
}
