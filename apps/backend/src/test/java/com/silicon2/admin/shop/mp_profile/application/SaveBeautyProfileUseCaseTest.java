package com.silicon2.admin.shop.mp_profile.application;

import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileRequest;
import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileResponse;
import com.silicon2.admin.shop.mp_profile.domain.model.BeautyProfile;
import com.silicon2.admin.shop.mp_profile.domain.repository.BeautyProfileRepository;
import com.silicon2.admin.testsupport.bdd.Bdd;
import com.silicon2.admin.testsupport.bdd.BddTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.Optional;

import static org.assertj.core.api.BDDAssertions.then;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

@BddTest
@DisplayName("SaveBeautyProfileUseCase")
class SaveBeautyProfileUseCaseTest {

    @Mock
    private BeautyProfileRepository repository;

    @InjectMocks
    private SaveBeautyProfileUseCase useCase;

    @Nested
    @DisplayName("프로필 저장 시")
    class WhenSavingProfile {

        @Test
        @DisplayName("신규 사용자이면 프로필을 생성한다")
        void shouldCreateNewProfile() {
            String userId = "newuser";
            BeautyProfileRequest request = requestWithLists();

            Bdd.given(() -> {
                given(repository.findByUserId(userId)).willReturn(Optional.empty());
                given(repository.save(any(BeautyProfile.class))).willAnswer(invocation -> {
                    BeautyProfile saved = invocation.getArgument(0);
                    saved.setId(1L);
                    saved.setCreatedAt(LocalDateTime.now());
                    saved.setUpdatedAt(LocalDateTime.now());
                    return saved;
                });
            });

            BeautyProfileResponse response = Bdd.when(() -> useCase.execute(userId, request));

            Bdd.then(() -> {
                then(response.getGender()).isEqualTo("FEMALE");
                then(response.getSkinConcern()).containsExactly("WRINKLES", "DULLNESS");

                ArgumentCaptor<BeautyProfile> captor = ArgumentCaptor.forClass(BeautyProfile.class);
                verify(repository).save(captor.capture());
                then(captor.getValue().getUserId()).isEqualTo(userId);
                then(captor.getValue().getSkinConcern()).isEqualTo("WRINKLES,DULLNESS");
            });
        }

        @Test
        @DisplayName("기존 사용자이면 프로필을 업데이트한다")
        void shouldUpdateExistingProfile() {
            String userId = "existinguser";
            BeautyProfile existing = new BeautyProfile();
            existing.setId(5L);
            existing.setUserId(userId);
            existing.setGender("MALE");

            BeautyProfileRequest request = new BeautyProfileRequest();
            request.setGender("MALE");
            request.setAgeGroup("40-49");
            request.setSkinType("COMBINATION");
            request.setSkinConcern(Arrays.asList("PORES"));
            request.setCleanBeautyPreferences(Arrays.asList("ORGANIC", "NATURAL"));

            Bdd.given(() -> {
                given(repository.findByUserId(userId)).willReturn(Optional.of(existing));
                given(repository.save(any(BeautyProfile.class))).willAnswer(invocation -> invocation.getArgument(0));
            });

            BeautyProfileResponse response = Bdd.when(() -> useCase.execute(userId, request));

            Bdd.then(() -> {
                then(response.getAgeGroup()).isEqualTo("40-49");
                then(response.getSkinConcern()).containsExactly("PORES");
                verify(repository).findByUserId(userId);
            });
        }

        @Test
        @DisplayName("빈 리스트는 빈 문자열로 저장한다")
        void shouldStoreEmptyListsAsEmptyString() {
            String userId = "user789";
            BeautyProfileRequest request = new BeautyProfileRequest();
            request.setGender("FEMALE");
            request.setSkinConcern(Collections.emptyList());
            request.setHealthConcern(null);

            Bdd.given(() -> {
                given(repository.findByUserId(userId)).willReturn(Optional.empty());
                given(repository.save(any(BeautyProfile.class))).willAnswer(invocation -> invocation.getArgument(0));
            });

            BeautyProfileResponse response = Bdd.when(() -> useCase.execute(userId, request));

            Bdd.then(() -> {
                then(response.getSkinConcern()).isEmpty();
                then(response.getHealthConcern()).isEmpty();
            });
        }
    }

    private BeautyProfileRequest requestWithLists() {
        BeautyProfileRequest request = new BeautyProfileRequest();
        request.setGender("FEMALE");
        request.setAgeGroup("30-39");
        request.setSkinType("DRY");
        request.setSkinConcern(Arrays.asList("WRINKLES", "DULLNESS"));
        request.setHealthConcern(Arrays.asList("HYDRATION"));
        request.setCleanBeautyPreferences(Arrays.asList("VEGAN"));
        request.setHairConcern(Arrays.asList("SPLIT_ENDS"));
        return request;
    }
}
