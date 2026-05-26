package com.silicon2.admin.shop.mp_profile.application;

import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileRequest;
import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileResponse;
import com.silicon2.admin.shop.mp_profile.domain.model.BeautyProfile;
import com.silicon2.admin.shop.mp_profile.domain.repository.BeautyProfileRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class SaveBeautyProfileUseCase {

    private final BeautyProfileRepository repository;

    public BeautyProfileResponse execute(String userId, BeautyProfileRequest request) {
        BeautyProfile profile = repository.findByUserId(userId)
                .orElseGet(() -> BeautyProfile.createForUser(userId));

        profile.updateAttributes(
                request.getGender(),
                request.getAgeGroup(),
                request.getSkinTone(),
                request.getSkinConcern(),
                request.getHealthConcern(),
                request.getCleanBeautyPreferences(),
                request.getSkinType(),
                request.getHairConcern()
        );

        return toResponse(repository.save(profile));
    }

    private BeautyProfileResponse toResponse(BeautyProfile profile) {
        BeautyProfileResponse response = new BeautyProfileResponse();
        response.setGender(profile.getGender());
        response.setAgeGroup(profile.getAgeGroup());
        response.setSkinTone(profile.getSkinTone());
        response.setSkinConcern(profile.getSkinConcernAsList());
        response.setHealthConcern(profile.getHealthConcernAsList());
        response.setCleanBeautyPreferences(profile.getCleanBeautyPreferencesAsList());
        response.setSkinType(profile.getSkinType());
        response.setHairConcern(profile.getHairConcernAsList());
        return response;
    }
}
