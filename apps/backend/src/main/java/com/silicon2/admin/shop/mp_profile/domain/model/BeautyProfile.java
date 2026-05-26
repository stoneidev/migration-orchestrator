package com.silicon2.admin.shop.mp_profile.domain.model;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class BeautyProfile {
    private Long id;
    private String userId;
    private String gender;
    private String ageGroup;
    private String skinTone;
    private String skinConcern;
    private String healthConcern;
    private String cleanBeautyPreferences;
    private String skinType;
    private String hairConcern;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
