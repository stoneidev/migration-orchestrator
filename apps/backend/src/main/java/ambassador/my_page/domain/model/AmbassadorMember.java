package com.silicon2.admin.ambassador.my_page.domain.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AmbassadorMember {
    private Long id;
    private Long memberId;
    private String status;
    private LocalDateTime approvedAt;
    private LocalDateTime bannedAt;
    private String banReason;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public boolean isActive() {
        return "ACTIVE".equals(status);
    }

    public boolean canAccessPage() {
        return isActive() && bannedAt == null;
    }
}
