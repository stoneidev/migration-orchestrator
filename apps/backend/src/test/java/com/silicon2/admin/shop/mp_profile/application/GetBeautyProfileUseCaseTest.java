package com.silicon2.admin.shop.mp_profile.application;

import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileResponse;
import com.silicon2.admin.shop.mp_profile.domain.model.BeautyProfile;
import com.silicon2.admin.shop.mp_profile.domain.repository.BeautyProfileRepository;
import com.silicon2.admin.testsupport.bdd.Bdd;
import com.silicon2.admin.testsupport.bdd.BddTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;

import java.time.LocalDateTime;
import java.util.Optional;

import static org.assertj.core.api.BDDAssertions.then;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

@BddTest
@DisplayName("GetBeautyProfileUseCase")
class GetBeautyProfileUseCaseTest {

    @Mock
    private BeautyProfileRepository repository;

    @InjectMocks
    private GetBeautyProfileUseCase useCase;

    @Nested
    @DisplayName("프로필 조회 시")
    class WhenGettingProfile {

        @Test
        @DisplayName("존재하는 사용자의 프로필을 반환한다")
        void shouldReturnExistingProfile() {
            Bdd.given(() -> {
                String userId = "user123";
                BeautyProfile profile = profileWithLists(userId);
                given(repository.findByUserId(userId)).willReturn(Optional.of(profile));
            });

            BeautyProfileResponse response = Bdd.when(() -> useCase.execute("user123"));

            Bdd.then(() -> {
                then(response).isNotNull();
                then(response.getGender()).isEqualTo("FEMALE");
                then(response.getSkinConcern()).containsExactly("ACNE", "WRINKLES");
                verify(repository).findByUserId("user123");
            });
        }

        @Test
        @DisplayName("존재하지 않는 사용자이면 null을 반환한다")
        void shouldReturnNullWhenProfileNotFound() {
            Bdd.given(() -> given(repository.findByUserId("nonexistent")).willReturn(Optional.empty()));

            BeautyProfileResponse response = Bdd.when(() -> useCase.execute("nonexistent"));

            Bdd.then(() -> {
                then(response).isNull();
                verify(repository).findByUserId("nonexistent");
            });
        }

        @Test
        @DisplayName("빈 문자열 필드는 빈 리스트로 변환한다")
        void shouldParseEmptyListFields() {
            Bdd.given(() -> {
                BeautyProfile profile = new BeautyProfile();
                profile.setUserId("user456");
                profile.setGender("MALE");
                profile.setSkinConcern("");
                profile.setHealthConcern(null);
                profile.setCreatedAt(LocalDateTime.now());
                profile.setUpdatedAt(LocalDateTime.now());
                given(repository.findByUserId("user456")).willReturn(Optional.of(profile));
            });

            BeautyProfileResponse response = Bdd.when(() -> useCase.execute("user456"));

            Bdd.then(() -> {
                then(response.getSkinConcern()).isEmpty();
                then(response.getHealthConcern()).isEmpty();
            });
        }
    }

    private BeautyProfile profileWithLists(String userId) {
        BeautyProfile profile = new BeautyProfile();
        profile.setId(1L);
        profile.setUserId(userId);
        profile.setGender("FEMALE");
        profile.setAgeGroup("20-29");
        profile.setSkinType("OILY");
        profile.setSkinConcern("ACNE,WRINKLES");
        profile.setHealthConcern("HYDRATION");
        profile.setCleanBeautyPreferences("VEGAN,CRUELTY_FREE");
        profile.setHairConcern("DANDRUFF");
        profile.setCreatedAt(LocalDateTime.now());
        profile.setUpdatedAt(LocalDateTime.now());
        return profile;
    }
}
