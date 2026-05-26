package com.silicon2.admin.shop.mp_profile.application;

import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileResponse;
import com.silicon2.admin.shop.mp_profile.domain.model.BeautyProfile;
import com.silicon2.admin.shop.mp_profile.domain.repository.BeautyProfileRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

@Service
@RequiredArgsConstructor
public class GetBeautyProfileUseCase {

    private final BeautyProfileRepository repository;

    public BeautyProfileResponse execute(String userId) {
        return repository.findByUserId(userId)
                .map(this::toResponse)
                .orElse(null);
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
