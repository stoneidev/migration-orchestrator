package com.silicon2.admin.member.wallet.adapter.out.persistence.mapper;

import com.silicon2.admin.member.wallet.adapter.out.persistence.entity.MemberWalletEntity;
import com.silicon2.admin.member.wallet.domain.model.Member;
import org.springframework.stereotype.Component;

@Component
public class MemberMapper {

    public Member toDomain(MemberWalletEntity entity) {
        if (entity == null) {
            return null;
        }

        return Member.builder()
                .id(entity.getId())
                .mbId(entity.getMbId())
                .mbPoint(entity.getMbPoint())
                .mbName(entity.getMbName())
                .mbEmail(entity.getMbEmail())
                .hasUsedCoupon(entity.getHasUsedCoupon())
                .couponCount(entity.getCouponCount())
                .build();
    }

    public MemberWalletEntity toEntity(Member domain) {
        if (domain == null) {
            return null;
        }

        return MemberWalletEntity.builder()
                .id(domain.getId())
                .mbId(domain.getMbId())
                .mbPoint(domain.getMbPoint())
                .mbName(domain.getMbName())
                .mbEmail(domain.getMbEmail())
                .hasUsedCoupon(domain.getHasUsedCoupon())
                .couponCount(domain.getCouponCount())
                .build();
    }
}
