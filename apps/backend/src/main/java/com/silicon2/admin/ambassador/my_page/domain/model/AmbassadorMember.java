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
    private String name;
    private String email;
    private String phoneNumber;
    private LocalDateTime joinedAt;
    private LocalDateTime bannedAt;
    private String banReason;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public boolean isActive() {
        return "ACTIVE".equals(status);
    }

    public boolean isBanned() {
        return "BANNED".equals(status);
    }

    public boolean canAccessMyPage() {
        return isActive() && bannedAt == null;
    }
}
