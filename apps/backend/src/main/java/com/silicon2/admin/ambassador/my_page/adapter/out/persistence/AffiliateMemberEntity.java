package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "affiliate_member")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AffiliateMemberEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "ambassador_member_id", nullable = false)
    private Long ambassadorMemberId;

    @Column(name = "affiliate_code", nullable = false, length = 50, unique = true)
    private String affiliateCode;

    @Column(name = "tracking_code", nullable = false, length = 50, unique = true)
    private String trackingCode;

    @Column(name = "is_active", nullable = false)
    private Boolean isActive;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
