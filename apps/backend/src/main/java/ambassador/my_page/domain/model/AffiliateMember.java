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
public class AffiliateMember {
    private Long id;
    private Long memberId;
    private String trackingCode;
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
