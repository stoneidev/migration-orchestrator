package com.silicon2.admin.shop.mp_profile.application;

import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileResponse;
import com.silicon2.admin.shop.mp_profile.domain.model.BeautyProfile;
import com.silicon2.admin.shop.mp_profile.domain.repository.BeautyProfileRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.time.LocalDateTime;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

@DisplayName("GetBeautyProfileUseCase 테스트")
class GetBeautyProfileUseCaseTest {

    @Mock
    private BeautyProfileRepository repository;

    @InjectMocks
    private GetBeautyProfileUseCase useCase;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    @DisplayName("존재하는 사용자의 프로필을 조회한다")
    void testExecute_ExistingProfile() {
        // given
        String userId = "user123";
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

        given(repository.findByUserId(userId)).willReturn(Optional.of(profile));

        // when
        BeautyProfileResponse response = useCase.execute(userId);

        // then
        assertThat(response).isNotNull();
        assertThat(response.getGender()).isEqualTo("FEMALE");
        assertThat(response.getAgeGroup()).isEqualTo("20-29");
        assertThat(response.getSkinType()).isEqualTo("OILY");
        assertThat(response.getSkinConcern()).containsExactly("ACNE", "WRINKLES");
        assertThat(response.getHealthConcern()).containsExactly("HYDRATION");
        assertThat(response.getCleanBeautyPreferences()).containsExactly("VEGAN", "CRUELTY_FREE");
        assertThat(response.getHairConcern()).containsExactly("DANDRUFF");

        verify(repository).findByUserId(userId);
    }

    @Test
    @DisplayName("존재하지 않는 사용자 조회 시 null을 반환한다")
    void testExecute_NonExistingProfile() {
        // given
        String userId = "nonexistent";
        given(repository.findByUserId(userId)).willReturn(Optional.empty());

        // when
        BeautyProfileResponse response = useCase.execute(userId);

        // then
        assertThat(response).isNull();
        verify(repository).findByUserId(userId);
    }

    @Test
    @DisplayName("빈 문자열 필드는 빈 리스트로 파싱된다")
    void testExecute_EmptyStringFields() {
        // given
        String userId = "user456";
        BeautyProfile profile = new BeautyProfile();
        profile.setUserId(userId);
        profile.setGender("MALE");
        profile.setSkinConcern("");
        profile.setHealthConcern(null);
        profile.setCleanBeautyPreferences("");
        profile.setHairConcern(null);
        profile.setCreatedAt(LocalDateTime.now());
        profile.setUpdatedAt(LocalDateTime.now());

        given(repository.findByUserId(userId)).willReturn(Optional.of(profile));

        // when
        BeautyProfileResponse response = useCase.execute(userId);

        // then
        assertThat(response).isNotNull();
        assertThat(response.getSkinConcern()).isEmpty();
        assertThat(response.getHealthConcern()).isEmpty();
        assertThat(response.getCleanBeautyPreferences()).isEmpty();
        assertThat(response.getHairConcern()).isEmpty();
    }
}
