package com.silicon2.admin.ambassador.my_page.adapter.out.persistence.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "ambassador_member_sns")
@Getter
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

    @Column(name = "sns_account_id", length = 100)
    private String snsAccountId;

    @Column(name = "sns_account_name", length = 100)
    private String snsAccountName;

    @Column(name = "created_at")
    private LocalDateTime createdAt;
}
