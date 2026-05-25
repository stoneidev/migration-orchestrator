package com.silicon2.admin.shop.mp_profile.application.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class BeautyProfileResponse {
    private String gender;
    private String ageGroup;
    private String skinTone;
    private List<String> skinConcern;
    private List<String> healthConcern;
    private List<String> cleanBeautyPreferences;
    private String skinType;
    private List<String> hairConcern;
}
