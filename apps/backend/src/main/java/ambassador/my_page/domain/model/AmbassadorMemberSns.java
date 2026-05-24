package com.silicon2.admin.ambassador.my_page.domain.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AmbassadorMemberSns {
    private Long id;
    private Long ambassadorMemberId;
    private String snsType;
    private String snsHandle;
    private String snsUrl;
    private Integer followerCount;
    private Boolean isPrimary;
    private LocalDateTime verifiedAt;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
