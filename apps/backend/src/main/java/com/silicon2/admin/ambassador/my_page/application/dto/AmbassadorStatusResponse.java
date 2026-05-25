package com.silicon2.admin.ambassador.my_page.application.dto;

import com.silicon2.admin.ambassador.my_page.domain.model.AmbassadorStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.util.List;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AmbassadorStatusResponse {
    private Long memberId;
    private AmbassadorStatus status;
    private String trackingCode;
    private boolean canAccess;
    private AmbassadorProfile profile;
    private List<SocialChannel> socialChannels;
    private List<AmbassadorReward> rewards;

    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AmbassadorProfile {
        private String name;
        private String country;
        private String birthDate;
        private String skinType;
    }

    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SocialChannel {
        private String name;
        private String platform;
        private String icon;
    }

    @Getter
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AmbassadorReward {
        private String icon;
        private String title;
        private String description;
    }
}
