package com.silicon2.admin.ambassador.my_page.adapter.out.persistence;

import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.entity.AmbassadorMemberEntity;
import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.entity.AmbassadorMemberSnsEntity;
import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorStatus;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component
@Profile("nomysql")
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {

    private final AmbassadorMemberJpaRepository memberRepository;
    private final AmbassadorMemberSnsJpaRepository snsRepository;

    @Override
    public void run(String... args) {
        AmbassadorMemberEntity member = new AmbassadorMemberEntity();
        member.setMemberId(1L);
        member.setStatus(AmbassadorStatus.ACTIVE);
        member.setTrackingCode("AMB-STK-001");
        member.setJoinedAt(LocalDateTime.now().minusMonths(3));
        member.setUpdatedAt(LocalDateTime.now());
        memberRepository.save(member);

        AmbassadorMemberSnsEntity sns1 = new AmbassadorMemberSnsEntity();
        sns1.setAmbassadorMemberId(member.getId());
        sns1.setSnsType("instagram");
        sns1.setSnsAccountId("@stylekorean_ambassador");
        sns1.setSnsAccountName("StyleKorean Official");
        sns1.setCreatedAt(LocalDateTime.now());
        snsRepository.save(sns1);

        AmbassadorMemberSnsEntity sns2 = new AmbassadorMemberSnsEntity();
        sns2.setAmbassadorMemberId(member.getId());
        sns2.setSnsType("youtube");
        sns2.setSnsAccountId("UCstylekorean");
        sns2.setSnsAccountName("StyleKorean Beauty");
        sns2.setCreatedAt(LocalDateTime.now());
        snsRepository.save(sns2);

        System.out.println("✓ Test data initialized: Ambassador member + 2 SNS accounts");
    }
}
