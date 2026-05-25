package com.silicon2.admin.ambassador.my_page.application;

import com.silicon2.admin.ambassador.my_page.application.dto.AmbassadorStatusResponse;
import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.AmbassadorMemberSnsJpaRepository;
import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.entity.AmbassadorMemberEntity;
import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.entity.AmbassadorMemberSnsEntity;
import com.silicon2.admin.ambassador.my_page.adapter.out.persistence.AmbassadorMemberJpaRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class CheckAmbassadorStatusUseCase {

    private final AmbassadorMemberJpaRepository ambassadorMemberRepository;
    private final AmbassadorMemberSnsJpaRepository ambassadorMemberSnsRepository;

    public AmbassadorStatusResponse execute(Long memberId) {
        AmbassadorMemberEntity member = ambassadorMemberRepository.findByMemberId(memberId)
                .orElseThrow(() -> new IllegalArgumentException("Ambassador not found"));

        List<AmbassadorMemberSnsEntity> snsEntities = ambassadorMemberSnsRepository.findByAmbassadorMemberId(member.getId());

        AmbassadorStatusResponse.AmbassadorProfile profile = AmbassadorStatusResponse.AmbassadorProfile.builder()
                .name("StyleKorean Ambassador")
                .country("Korea")
                .birthDate("1995-03-15")
                .skinType("Combination")
                .build();

        List<AmbassadorStatusResponse.SocialChannel> socialChannels = snsEntities.stream()
                .map(sns -> AmbassadorStatusResponse.SocialChannel.builder()
                        .name(sns.getSnsAccountName())
                        .platform(sns.getSnsType())
                        .icon(getIconForPlatform(sns.getSnsType()))
                        .build())
                .toList();

        List<AmbassadorStatusResponse.AmbassadorReward> rewards = List.of(
                AmbassadorStatusResponse.AmbassadorReward.builder()
                        .icon("🎁")
                        .title("Free Products")
                        .description("Monthly skincare boxes")
                        .build(),
                AmbassadorStatusResponse.AmbassadorReward.builder()
                        .icon("💰")
                        .title("Commission")
                        .description("15% on sales via your link")
                        .build()
        );

        return AmbassadorStatusResponse.builder()
                .profile(profile)
                .socialChannels(socialChannels)
                .rewards(rewards)
                .build();
    }

    private String getIconForPlatform(String platform) {
        return switch (platform.toLowerCase()) {
            case "instagram" -> "📷";
            case "youtube" -> "🎥";
            case "tiktok" -> "🎵";
            default -> "🌐";
        };
    }
}
