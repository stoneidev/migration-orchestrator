package com.silicon2.admin.ambassador.my_page.adapter.out.persistence.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "ambassador_campaign_image")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AmbassadorCampaignImageEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "ambassador_member_id", nullable = false)
    private Long ambassadorMemberId;

    @Column(name = "campaign_id", nullable = false)
    private Long campaignId;

    @Column(name = "image_url", nullable = false, length = 1000)
    private String imageUrl;

    @Column(name = "display_order")
    private Integer displayOrder;

    @Column(name = "image_type", length = 50)
    private String imageType;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
