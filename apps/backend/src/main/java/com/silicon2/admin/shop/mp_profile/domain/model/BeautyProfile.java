package com.silicon2.admin.shop.mp_profile.domain.model;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

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

    public static BeautyProfile createForUser(String userId) {
        BeautyProfile profile = new BeautyProfile();
        profile.setUserId(userId);
        return profile;
    }

    public void updateAttributes(
            String gender,
            String ageGroup,
            String skinTone,
            List<String> skinConcern,
            List<String> healthConcern,
            List<String> cleanBeautyPreferences,
            String skinType,
            List<String> hairConcern
    ) {
        this.gender = gender;
        this.ageGroup = ageGroup;
        this.skinTone = skinTone;
        this.skinConcern = joinList(skinConcern);
        this.healthConcern = joinList(healthConcern);
        this.cleanBeautyPreferences = joinList(cleanBeautyPreferences);
        this.skinType = skinType;
        this.hairConcern = joinList(hairConcern);
    }

    public List<String> getSkinConcernAsList() {
        return parseList(skinConcern);
    }

    public List<String> getHealthConcernAsList() {
        return parseList(healthConcern);
    }

    public List<String> getCleanBeautyPreferencesAsList() {
        return parseList(cleanBeautyPreferences);
    }

    public List<String> getHairConcernAsList() {
        return parseList(hairConcern);
    }

    private static String joinList(List<String> list) {
        if (list == null || list.isEmpty()) {
            return "";
        }
        return String.join(",", list);
    }

    private static List<String> parseList(String value) {
        if (value == null || value.isEmpty()) {
            return Collections.emptyList();
        }
        return Arrays.asList(value.split(","));
    }
}
