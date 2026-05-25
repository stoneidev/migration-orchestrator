package com.silicon2.admin.ambassador.my_page.domain.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AmbassadorMemberSns {
    private Long id;
    private Long ambassadorMemberId;
    private String snsType;
    private String snsAccountId;
    private String snsAccountName;
    private LocalDateTime linkedAt;
    private boolean isActive;
}
