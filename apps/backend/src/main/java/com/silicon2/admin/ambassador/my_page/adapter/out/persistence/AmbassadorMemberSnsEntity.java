package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "ambassador_member_sns")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AmbassadorMemberSnsEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "ambassador_member_id", nullable = false)
    private Long ambassadorMemberId;

    @Column(name = "sns_type", nullable = false, length = 20)
    private String snsType;

    @Column(name = "sns_account_id", nullable = false, length = 100)
    private String snsAccountId;

    @Column(name = "sns_account_url", length = 500)
    private String snsAccountUrl;

    @Column(name = "follower_count")
    private Integer followerCount;

    @Column(name = "is_verified")
    private Boolean isVerified;

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
