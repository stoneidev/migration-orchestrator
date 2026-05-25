package com.silicon2.admin.ambassador.my_page.adapter.out.persistence.entity;

import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorStatus;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "ambassador_member")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AmbassadorMemberEntity {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "member_id", nullable = false)
    private Long memberId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 20)
    private AmbassadorStatus status;

    @Column(name = "tracking_code", length = 50)
    private String trackingCode;

    @Column(name = "joined_at")
    private LocalDateTime joinedAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
