package com.silicon2.admin.member.wallet.application;

import com.silicon2.admin.member.wallet.application.dto.*;
import com.silicon2.admin.member.wallet.domain.repository.MemberRepository;
import com.silicon2.admin.member.wallet.domain.model.Member;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class GetWalletUseCase {

    private final MemberRepository memberRepository;

    @Transactional(readOnly = true)
    public WalletResponse execute(String mbId) {
        Member member = memberRepository.findByMbId(mbId)
                .orElseThrow(() -> new IllegalArgumentException("Member not found: " + mbId));

        MemberInfo memberInfo = MemberInfo.builder()
                .mbId(member.getMbId())
                .mbPoint(member.getMbPoint())
                .mbName(member.getMbName())
                .mbEmail(member.getMbEmail())
                .build();

        CouponUsageStatus couponStatus = CouponUsageStatus.builder()
                .mbId(member.getMbId())
                .hasUsedCoupon(member.getHasUsedCoupon())
                .couponCount(member.getCouponCount())
                .build();

        WalletData data = WalletData.builder()
                .member(memberInfo)
                .couponStatus(couponStatus)
                .build();

        return WalletResponse.builder()
                .success(true)
                .data(data)
                .build();
    }
}
