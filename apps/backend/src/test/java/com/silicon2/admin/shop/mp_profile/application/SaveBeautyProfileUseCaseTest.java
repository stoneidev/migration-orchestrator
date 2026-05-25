package com.silicon2.admin.shop.mp_profile.application;

import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileRequest;
import com.silicon2.admin.shop.mp_profile.application.dto.BeautyProfileResponse;
import com.silicon2.admin.shop.mp_profile.domain.BeautyProfile;
import com.silicon2.admin.shop.mp_profile.domain.BeautyProfileRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;

@DisplayName("SaveBeautyProfileUseCase 테스트")
class SaveBeautyProfileUseCaseTest {

    @Mock
    private BeautyProfileRepository repository;

    @InjectMocks
    private SaveBeautyProfileUseCase useCase;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    @DisplayName("새로운 프로필을 생성한다")
    void testExecute_CreateNewProfile() {
        // given
        String userId = "newuser";
        BeautyProfileRequest request = new BeautyProfileRequest();
        request.setGender("FEMALE");
        request.setAgeGroup("30-39");
        request.setSkinType("DRY");
        request.setSkinConcern(Arrays.asList("WRINKLES", "DULLNESS"));
        request.setHealthConcern(Arrays.asList("HYDRATION"));
        request.setCleanBeautyPreferences(Arrays.asList("VEGAN"));
        request.setHairConcern(Arrays.asList("SPLIT_ENDS"));

        given(repository.findByUserId(userId)).willReturn(Optional.empty());

        BeautyProfile savedProfile = new BeautyProfile();
        savedProfile.setId(1L);
        savedProfile.setUserId(userId);
        savedProfile.setGender(request.getGender());
        savedProfile.setAgeGroup(request.getAgeGroup());
        savedProfile.setSkinType(request.getSkinType());
        savedProfile.setSkinConcern("WRINKLES,DULLNESS");
        savedProfile.setHealthConcern("HYDRATION");
        savedProfile.setCleanBeautyPreferences("VEGAN");
        savedProfile.setHairConcern("SPLIT_ENDS");
        savedProfile.setCreatedAt(LocalDateTime.now());
        savedProfile.setUpdatedAt(LocalDateTime.now());

        given(repository.save(any(BeautyProfile.class))).willReturn(savedProfile);

        // when
        BeautyProfileResponse response = useCase.execute(userId, request);

        // then
        assertThat(response).isNotNull();
        assertThat(response.getGender()).isEqualTo("FEMALE");
        assertThat(response.getSkinType()).isEqualTo("DRY");
        assertThat(response.getSkinConcern()).containsExactly("WRINKLES", "DULLNESS");

        ArgumentCaptor<BeautyProfile> captor = ArgumentCaptor.forClass(BeautyProfile.class);
        verify(repository).save(captor.capture());
        BeautyProfile captured = captor.getValue();
        assertThat(captured.getUserId()).isEqualTo(userId);
        assertThat(captured.getSkinConcern()).isEqualTo("WRINKLES,DULLNESS");
    }

    @Test
    @DisplayName("기존 프로필을 업데이트한다")
    void testExecute_UpdateExistingProfile() {
        // given
        String userId = "existinguser";
        BeautyProfile existingProfile = new BeautyProfile();
        existingProfile.setId(5L);
        existingProfile.setUserId(userId);
        existingProfile.setGender("MALE");
        existingProfile.setSkinType("OILY");

        BeautyProfileRequest request = new BeautyProfileRequest();
        request.setGender("MALE");
        request.setAgeGroup("40-49");
        request.setSkinType("COMBINATION");
        request.setSkinConcern(Arrays.asList("PORES"));
        request.setHealthConcern(Collections.emptyList());
        request.setCleanBeautyPreferences(Arrays.asList("ORGANIC", "NATURAL"));
        request.setHairConcern(Collections.emptyList());

        given(repository.findByUserId(userId)).willReturn(Optional.of(existingProfile));

        BeautyProfile updatedProfile = new BeautyProfile();
        updatedProfile.setId(5L);
        updatedProfile.setUserId(userId);
        updatedProfile.setGender(request.getGender());
        updatedProfile.setAgeGroup(request.getAgeGroup());
        updatedProfile.setSkinType(request.getSkinType());
        updatedProfile.setSkinConcern("PORES");
        updatedProfile.setHealthConcern("");
        updatedProfile.setCleanBeautyPreferences("ORGANIC,NATURAL");
        updatedProfile.setHairConcern("");
        updatedProfile.setCreatedAt(LocalDateTime.now());
        updatedProfile.setUpdatedAt(LocalDateTime.now());

        given(repository.save(any(BeautyProfile.class))).willReturn(updatedProfile);

        // when
        BeautyProfileResponse response = useCase.execute(userId, request);

        // then
        assertThat(response).isNotNull();
        assertThat(response.getAgeGroup()).isEqualTo("40-49");
        assertThat(response.getSkinType()).isEqualTo("COMBINATION");
        assertThat(response.getSkinConcern()).containsExactly("PORES");
        assertThat(response.getCleanBeautyPreferences()).containsExactly("ORGANIC", "NATURAL");

        verify(repository).findByUserId(userId);
        verify(repository).save(any(BeautyProfile.class));
    }

    @Test
    @DisplayName("빈 리스트는 빈 문자열로 저장된다")
    void testExecute_EmptyLists() {
        // given
        String userId = "user789";
        BeautyProfileRequest request = new BeautyProfileRequest();
        request.setGender("FEMALE");
        request.setSkinConcern(Collections.emptyList());
        request.setHealthConcern(null);
        request.setCleanBeautyPreferences(Collections.emptyList());
        request.setHairConcern(null);

        given(repository.findByUserId(userId)).willReturn(Optional.empty());

        BeautyProfile savedProfile = new BeautyProfile();
        savedProfile.setUserId(userId);
        savedProfile.setGender("FEMALE");
        savedProfile.setSkinConcern("");
        savedProfile.setHealthConcern("");
        savedProfile.setCleanBeautyPreferences("");
        savedProfile.setHairConcern("");
        savedProfile.setCreatedAt(LocalDateTime.now());
        savedProfile.setUpdatedAt(LocalDateTime.now());

        given(repository.save(any(BeautyProfile.class))).willReturn(savedProfile);

        // when
        BeautyProfileResponse response = useCase.execute(userId, request);

        // then
        assertThat(response).isNotNull();
        assertThat(response.getSkinConcern()).isEmpty();
        assertThat(response.getHealthConcern()).isEmpty();
        assertThat(response.getCleanBeautyPreferences()).isEmpty();
        assertThat(response.getHairConcern()).isEmpty();
    }
}
