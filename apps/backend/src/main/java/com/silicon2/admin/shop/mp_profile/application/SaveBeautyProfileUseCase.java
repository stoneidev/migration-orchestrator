package com.silicon2.admin.shop.mp_profile.application;

import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileRequest;
import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileResponse;
import com.silicon2.admin.shop.mp_profile.domain.BeautyProfile;
import com.silicon2.admin.shop.mp_profile.domain.BeautyProfileRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class SaveBeautyProfileUseCase {

    private final BeautyProfileRepository repository;

    public BeautyProfileResponse execute(String userId, BeautyProfileRequest request) {
        BeautyProfile profile = repository.findByUserId(userId)
                .orElse(new BeautyProfile());

        profile.setUserId(userId);
        profile.setGender(request.getGender());
        profile.setAgeGroup(request.getAgeGroup());
        profile.setSkinTone(request.getSkinTone());
        profile.setSkinConcern(joinList(request.getSkinConcern()));
        profile.setHealthConcern(joinList(request.getHealthConcern()));
        profile.setCleanBeautyPreferences(joinList(request.getCleanBeautyPreferences()));
        profile.setSkinType(request.getSkinType());
        profile.setHairConcern(joinList(request.getHairConcern()));

        BeautyProfile saved = repository.save(profile);
        return toResponse(saved);
    }

    private String joinList(List<String> list) {
        if (list == null || list.isEmpty()) {
            return "";
        }
        return String.join(",", list);
    }

    private BeautyProfileResponse toResponse(BeautyProfile profile) {
        BeautyProfileResponse response = new BeautyProfileResponse();
        response.setGender(profile.getGender());
        response.setAgeGroup(profile.getAgeGroup());
        response.setSkinTone(profile.getSkinTone());
        response.setSkinConcern(parseList(profile.getSkinConcern()));
        response.setHealthConcern(parseList(profile.getHealthConcern()));
        response.setCleanBeautyPreferences(parseList(profile.getCleanBeautyPreferences()));
        response.setSkinType(profile.getSkinType());
        response.setHairConcern(parseList(profile.getHairConcern()));
        return response;
    }

    private List<String> parseList(String value) {
        if (value == null || value.isEmpty()) {
            return Collections.emptyList();
        }
        return Arrays.asList(value.split(","));
    }
}
