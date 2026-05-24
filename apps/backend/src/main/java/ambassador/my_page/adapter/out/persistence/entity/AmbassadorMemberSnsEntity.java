package com.silicon2.admin.ambassador.my_page.adapter.out.persistence.entity;

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

    @Column(name = "sns_type", nullable = false, length = 50)
    private String snsType;

    @Column(name = "sns_handle", length = 100)
    private String snsHandle;

    @Column(name = "sns_url", length = 500)
    private String snsUrl;

    @Column(name = "follower_count")
    private Integer followerCount;

    @Column(name = "is_primary")
    private Boolean isPrimary;

    @Column(name = "verified_at")
    private LocalDateTime verifiedAt;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
