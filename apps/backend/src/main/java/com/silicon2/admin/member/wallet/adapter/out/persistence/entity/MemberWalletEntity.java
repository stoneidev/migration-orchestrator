package com.silicon2.admin.member.wallet.adapter.out.persistence.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "member_wallet")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MemberWalletEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "mb_id", nullable = false, unique = true, length = 50)
    private String mbId;

    @Column(name = "mb_point", nullable = false)
    private Integer mbPoint;

    @Column(name = "mb_name", length = 100)
    private String mbName;

    @Column(name = "mb_email", length = 100)
    private String mbEmail;

    @Column(name = "has_used_coupon", nullable = false)
    private Boolean hasUsedCoupon;

    @Column(name = "coupon_count")
    private Integer couponCount;
}
