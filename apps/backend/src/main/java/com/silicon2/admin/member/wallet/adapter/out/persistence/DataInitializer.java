package com.silicon2.admin.member.wallet.adapter.out.persistence;

import com.silicon2.admin.member.wallet.adapter.out.persistence.entity.MemberWalletEntity;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

@Component("walletDataInitializer")
@Profile("nomysql")
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {

    private final MemberJpaRepository memberRepository;

    @Override
    public void run(String... args) {
        // Test member with points
        MemberWalletEntity member1 = MemberWalletEntity.builder()
                .mbId("test_member")
                .mbPoint(5)
                .mbName("Test User")
                .mbEmail("test@stylekorean.com")
                .hasUsedCoupon(true)
                .couponCount(1)
                .build();
        memberRepository.save(member1);

        // Member with more points
        MemberWalletEntity member2 = MemberWalletEntity.builder()
                .mbId("power_user")
                .mbPoint(150)
                .mbName("Power User")
                .mbEmail("power@stylekorean.com")
                .hasUsedCoupon(true)
                .couponCount(5)
                .build();
        memberRepository.save(member2);

        // New member with no points
        MemberWalletEntity member3 = MemberWalletEntity.builder()
                .mbId("new_member")
                .mbPoint(0)
                .mbName("New User")
                .mbEmail("new@stylekorean.com")
                .hasUsedCoupon(false)
                .couponCount(0)
                .build();
        memberRepository.save(member3);

        // Member with expired points
        MemberWalletEntity member4 = MemberWalletEntity.builder()
                .mbId("expired_user")
                .mbPoint(0)
                .mbName("Expired User")
                .mbEmail("expired@stylekorean.com")
                .hasUsedCoupon(true)
                .couponCount(3)
                .build();
        memberRepository.save(member4);

        // VIP member
        MemberWalletEntity member5 = MemberWalletEntity.builder()
                .mbId("vip_member")
                .mbPoint(500)
                .mbName("VIP Customer")
                .mbEmail("vip@stylekorean.com")
                .hasUsedCoupon(true)
                .couponCount(12)
                .build();
        memberRepository.save(member5);

        System.out.println("✓ Wallet test data initialized: 5 members with varied balances");
    }
}
