package com.silicon2.admin.ambassador.my_page.application.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AmbassadorStatusResponse {
    private Long ambassadorId;
    private String status;
    private String name;
    private String email;
    private Boolean hasAffiliate;
    private List<SnsAccountDto> snsAccounts;
    private LocalDateTime joinedAt;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SnsAccountDto {
        private Long id;
        private String snsType;
        private String accountId;
        private String accountUrl;
        private Integer followerCount;
        private Boolean isVerified;
    }
}
